// Ground truth: every call `recv.field...Method(...)` whose callee is a concrete method
// declared inside the analyzed module, resolved by go/types.
package main

import (
	"encoding/json"
	"fmt"
	"go/ast"
	"go/types"
	"os"
	"path/filepath"
	"strings"

	"golang.org/x/tools/go/packages"
)

type Row struct {
	File, CalleeFile, Callee, Kind string
	Line                           int
	ViaField                       bool
}

func main() {
	root, _ := filepath.Abs(os.Args[1])
	cfg := &packages.Config{Mode: packages.NeedName | packages.NeedFiles | packages.NeedSyntax | packages.NeedTypes | packages.NeedTypesInfo | packages.NeedModule, Dir: root, Tests: false}
	pkgs, err := packages.Load(cfg, "./...")
	if err != nil { panic(err) }
	var rows []Row
	for _, p := range pkgs {
		for _, f := range p.Syntax {
			fname := p.Fset.Position(f.Pos()).Filename
			rel, _ := filepath.Rel(root, fname)
			ast.Inspect(f, func(n ast.Node) bool {
				call, ok := n.(*ast.CallExpr)
				if !ok { return true }
				sel, ok := call.Fun.(*ast.SelectorExpr)
				if !ok { return true }
				s := p.TypesInfo.Selections[sel]
				if s == nil || s.Kind() != types.MethodVal { return true }
				fn, ok := s.Obj().(*types.Func)
				if !ok { return true }
				recv := fn.Type().(*types.Signature).Recv()
				if recv != nil { if _, isIface := recv.Type().Underlying().(*types.Interface); isIface { return true } }
				if len(s.Index()) > 1 { return true } // promoted via embedding: separate known issue
				pos := p.Fset.Position(fn.Pos())
				if !strings.HasPrefix(pos.Filename, root) { return true }
				crel, _ := filepath.Rel(root, pos.Filename)
				// is operand a field selection (x.f.M) ?
				via := false
				if inner, ok := sel.X.(*ast.SelectorExpr); ok {
					if is := p.TypesInfo.Selections[inner]; is != nil && is.Kind() == types.FieldVal { via = true }
				}
				rows = append(rows, Row{filepath.ToSlash(rel), filepath.ToSlash(crel), fn.FullName(), "method", p.Fset.Position(call.Pos()).Line, via})
				return true
			})
		}
	}
	b, _ := json.Marshal(rows)
	fmt.Println(string(b))
}
