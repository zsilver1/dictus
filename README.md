# Markdown Modified Syntax

### Creating Words

Any `H1` (i.e. a line beginning wth `# `) will be treated as the start of a new
word. All text until the next `H1`, including all definitions, will be grouped
with the current word. Any captured properties or text that are not inside of a
definition will be associated with the word itself.

### Creating Definitions

Creating a definition is as simple as inserting a line with three dashes
`---`. This marks the beginning of a definition. All following captured
properties and text will be associated with the current definition until a new
word or definition is encountered.

### Capturing Properties

**Note**: Capturing only works if the below strings are on their own line.

`${key: value}` - Captures `value` (auto trims whitespace).

`${key: list, of, values}` - Captures `list, of, values`.


### Linking to Words:

`[[word]]` - Creates a link to `word` in the same file.

`[[language:word]]` - Creates a link to `word` in another language file. With
"dwim" mode will fuzzy match the language file if no exact match
found. (E.g. with languages `test` and `proto-test`, using `prot` as a language
key would match with `proto-test`.)
