# Custom Fonts

Drop any `.flf` figlet font file here to make it available in the CLI.

```bash
text2ascii "Hello" --font myfont
```

## Where to find fonts

- [patorjk.com/software/taag](http://patorjk.com/software/taag) — online preview tool
- [figlet.org/fontdb.cgi](http://www.figlet.org/fontdb.cgi) — official font archive
- [github.com/xero/figlet-fonts](https://github.com/xero/figlet-fonts) — community collection

## Notes

- Font files must have the `.flf` extension
- Font names are case-insensitive when using `--font`
- pyfiglet also includes 550+ built-in fonts — run `text2ascii --list-fonts` to see all of them
