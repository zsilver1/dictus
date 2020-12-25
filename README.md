
# Dictus

## Input Format

### Metadata
All language files can optionally start with a `metadata` object. Any fields in the metadata object will be available inside the `Language` object in jinja. The following metadata fields have special properties:
* `display_name: str` - the name of the language to be displayed at the top of the page
* `order: int` - for pages with multiple languages, this will determine the order in the language list

### Schema
`Lemma` (the name of the object is the lemma's name):
* `defs: List[Definition]`
* `text: str`
* `tags: List[str]`

`Definition`:
* `pos: Union[str, List[str]]` - definition's part(s) of speech
* `glosses: List[str]` - simple translations, used for searching
* `text: str`
* `tags: List[str]`
* `links: List[Link]` - list of links to other words/definitions (see below)

A `Link` is simply a map from a `str` "link type" to a list of `str` "link locations." (For example, a link type could be "related words" or "synonyms.") A link location has the following format:
`{language}:lemma:{definition index}`.
The `language` portion only needs to be specified if linking to a lemma in another language. The definition index may also be left blank, it will default to `1`.

#### Link Examples:
* `cheese` - will link to the first definition of the lemma "cheese" in the same language file.
* `cheese:2` - will link to the second definition of the lemma "cheese" in the same language file.
* `proto-lang:cheese` - will link to the first definition of the lemma "cheese" in the language "proto-lang".
* `proto-lang:cheese:2` - will link to the second definition of the lemma "cheese" in the language "proto-lang".
**Note**: Language names in links are fuzzy matched, so in the above example writing `proto` instead of `proto-lang` would also work, assuming there's only one language with `proto` in its name.
**Note 2**: The `text` field in a Lemma or Definition may also have links. They must simply be enclosed in two square brackets, e.g. 
`[[proto-lang:cheese:2]]`


### Word Example
Below is an example word in yaml format:
```yaml
karu:
  defs:
    -
      pos: n
      glosses:
        - this
        - is a
        - test
      links:
        source: [karu:1, otherlang:nita:1]
        related: otherlang:karua
      text: |
        This is some more example text [[test:1]]

        **bold**

        | a | b |
        |---|---|
        | c | d |
    
    - # a second definition
      pos: v
      glosses: [just one]
      links:
        related: [cheese:karua]
```


## Jinja2 Objects Available

`lang` is the top level object by which one can access all of a language's data. The `lang` variable has the following built-in fields:
* `lemmas` - a list of `Lemma` objects
* `pos_set` - a set of unique parts of speech for the language
* `name` - the name of the file the language appears in
* `display_name` - the display name of the language
* `order` - the order the language should appear in the language list
**Note**: the language object will also automatically be populated with *all* fields in the `metadata` section of the input file (see above).

`Lemma` objects have the following build-in fields:
* `name` - the name of the lemma
* `text` - text associated with the lemma
* `defs` - list of `Definition` objects
* `tags` - list of `str` tags
Like the lang object above, lemma objects will also be automatically populated with any addition fields from the input file.

`Definition` objects have the following build-in fields:
* `pos` - list of all parts of speech for the definition
* `glosses` - list of glosses
* `text` - text associated with the definition
* `link_groups` - list of `LinkGroup` objects
* `backlink_groups` - list of `LinkGroup` objects for all links pointing to the definition
Like the lang object above, definition objects will also be automatically populated with any addition fields from the input file.

`LinkGroup` objects have have the following fields:
* `type` - a `str` link type (e.g. "etymology", etc.)
* `links` - a list of link objects, each of which contains the link's destination `lang`, `lemma`, and `def_index` as well as a `url` field pointing to the destination.
