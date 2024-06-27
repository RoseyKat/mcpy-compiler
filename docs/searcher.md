# Searcher
`searcher.json` will find and replace keywords. This can come in handy for emojis, text coloring, and anything you can think of. Simply place a file called `searcher.json` at the root of your project.

This is entirely optional and can be toggled in the config.

```jsonc
[
    {
        "search": "foo", // What keyword to search for in a given file.
        "replace_with": "bar", // What to replace `search` with.
        "file_types": [ // Type of files to perform action on. If you want all files, then omit adding `file_types`
            {"startswith": "BP/items", "endswith": ".json"} // What the filepath should start with and end with to perform action. At least one can be present, both do not need to be present.
        ]
    }
]
```