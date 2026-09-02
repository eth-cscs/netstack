[](){#ref-contributing}
# Contributing

This documentation uses the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) framework.

## Before starting

Read the [guidelines][] and [style guide][] before you make a contribution.
Consistent style and common practices make the documentation easier for users to read and navigate.
They also make the documentation easier for regular contributors to write, and they avoid style debates.
The guidelines leave room for personal style. You can write in a style that feels natural to you.

Review your edits against the [Guidelines][ref-contributing-guidelines] section below.

!!! note
    A simple editor markdown preview may not render all the features of the documentation.

To review the docs locally, use the `serve` script in the root of the repository, as shown below:
```bash
./serve
...
INFO    -  [08:33:34] Serving on http://127.0.0.1:8000/
```

!!! note
    To run the serve script, you must first install [uv](https://docs.astral.sh/uv/getting-started/installation/).

[](){#ref-contributing-guidelines}
## Guidelines

### Links

#### External links

Links to external sites use the `[]()` syntax:

=== "external link syntax"

    ```
    [The Spack repository](https://github.com/spack/spack)
    ```

=== "result"

    [The Spack repository](https://github.com/spack/spack)

#### Internal links

You must take care when you add and maintain links to internal pages and sections. The links must not break or conflict with each other.
You can link to other files with relative links, for example `\[the fast server](../servers.md#fast-server)`. But if the target file moves, or if the section title "fast-server" changes, the link breaks.

Instead, add a unique reference to each section.

=== "adding a reference"

    Add a reference above the item. In this example, the reference links to the section titled `## The fast server`:

    ```
    [](){#ref-fast-server}
    ## Fast server
    ```

    Use the `[](){#}` syntax to define the reference/anchor.

    !!! note
        Always place the anchor above the item you are linking to.

=== "linking to a reference"

    In any other file in the project, use the `[][]` syntax to refer to the link. This link type uses square brackets, not parentheses:

    ```
    [the fast server][ref-fast-server]
    ```

Reference names follow a convention. This convention keeps names unique across the whole documentation automatically:

1. A page reference starts with `ref-`, followed by the file path. Remove the `docs/` prefix and the `.md` suffix from the path, and replace slashes with hyphens. For example, `docs/tools.md` becomes `ref-tools`.
    - Pages under `docs/packages` are an exception. They drop the directory name. For example, `docs/packages/libfabric.md` becomes `ref-pkg-libfabric`.
2. An `index.md` page drops the file name. For example, `docs/analysis/index.md` becomes `ref-analysis`.
3. A section reference extends the page reference with a slug of the section title. For example, the `## user-stack` section of `docs/tools.md` has the reference `ref-tools-user-stack`.

Every page carries its page reference immediately above the title.
This way, you can link to any page without using a relative path. You can also move pages between directories, and the links that point to them still work.

Add a section reference when something links to that section, or when a link to it is likely.
Do not add a reference above every heading as a matter of course. Unused references are noise in the source, and they are one more thing to keep consistent.

This approach protects links from breaking. A link keeps working even when:

* the file that contains the link moves, or the file it points to moves, or
* the title of the target section changes.

### Images

> An image often explains an idea faster than text.

Use images to improve clarity and understanding.
You can use **screenshots** or **diagrams**.

Store images in the `docs/images` directory.

* Create a new sub-directory for your images when appropriate.
* Choose a path and file name that describe the image content. Do not use vague names like `screenshot.png` or `PX-202502025-imgx.png`.

!!! warning
    Keep the size of your images small. This keeps the repository lightweight.


#### Screenshots

Screenshots are not appropriate for this project.

#### Diagrams

Diagrams can help readers understand more abstract concepts like processes or architectures.
Use [mermaid](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams#creating-mermaid-diagrams) for diagrams.
That format makes diagrams easy to maintain. It also removes the need to commit image files to the repository.

??? "Example"

    === "Source"

        ````text
        ```mermaid
        graph TD;
            Image(Will image add value?);
            Image--NO-->T(keep text only);
            Image--YES-->SD(What image is needed?)
            SD--Screenshot-->S(keep it lean)
            SD--Diagram-->D(keep it maintainable)
            D--Default-->M(Mermaid)
            D--Custom-->DR(Draw.io)
        ```
        ````

    === "Rendered"

        ```mermaid
        graph TD;
            Image(Will image add value?);
            Image--NO-->T(keep text only);
            Image--YES-->SD(What image is needed?)
            SD--Screenshot-->S(keep it lean)
            SD--Diagram-->D(keep it maintainable)
            D--Default-->M(Mermaid)
            D--Custom-->DR(Draw.io)
        ```

For hand-crafted diagrams, use [draw.io](https://www.drawio.com/).
Export the PNG with the [source inside](https://www.drawio.com/doc/faq/export-to-png). Name the file `file.drawio.png` by convention. This lets you edit the diagram again later.

### Text formatting

Turn off automatic line breaks in your text editor. Write one sentence per line in paragraphs of text.

The examples below show what happens to line breaks when you edit a sentence:

=== "good"
    Before:
    ```
    There are many different versions of MPI that can be used for communication.
    The final choice of which to use is up to you.
    ```

    After:
    ```
    There are many different versions of the popular MPI communication library that can be used for communication.
    The final choice of which to use is up to you.
    ```

    The diff in this case affects only one line.

=== "bad"
    Before:
    ```
    There are many different versions of MPI that
    can be used for communication. The final choice
    of which to use is up to you.
    ```

    After:
    ```
    There are many different versions of the popular
    MPI communication library that can be used for
    communication. The final choice of which to use
    is up to you.
    ```

    The diff in this case affects the original three lines. It also creates a new line.

This method defines a single standard way to write a paragraph of text. This approach works well with git.

* Changes to the text are less likely to create merge conflicts.
* When you change one line of text, the surrounding lines do not change, as in the example above.
* Diffs and history are easier to read.

### Frequently asked questions

The documentation does not have a FAQ section. The main documentation answers questions better than a separate FAQ section can.
You must take care when you add information to the main documentation. You must find where the information belongs, and edit the surrounding documentation.
You can add information to a FAQ more easily instead. But this splits information about one topic between the main docs and FAQ questions. This makes the documentation harder to search.

## Style guide

This section gives guidelines for how to format and present documentation in this repository.
Follow them in most cases. You can break a guideline, but only _for good reason_.

[](){#ref-contributing-voice}
### Voice

Write plainly.
This documentation follows [ASD-STE100](https://en.wikipedia.org/wiki/Simplified_Technical_English) (Simplified Technical English), a controlled-language standard for technical writing.
Apply these rules to every sentence you write:

* Write short sentences. Keep each sentence to one idea. Split a long sentence into two short ones instead of joining clauses with "which", "and", or a dash.
* Use active voice. Name the subject that performs the action.
  Write "Cray MPICH resolves libfabric through an rpath", not "libfabric is resolved by Cray MPICH through an rpath".
* Use the present tense for facts and descriptions.
* Use "must" for an obligation and "must not" for a prohibition. Do not use "should", "has to" or "ought to".
  Use "can" for a capability. Do not use "may", because "may" can mean either permission or possibility.
* Do not use an "-ing" word as a noun. Write "to clean the cache", not "for cleaning the cache".
* Do not string more than two or three nouns together. Add a preposition or an article to break up the string.
  Write "the interface between the driver and the network", not "the driver network connection interface".
* Keep articles such as "a" and "the". Do not drop them to save words.
* Do not use vague words such as "effectively", "basically", "clearly", "obviously" or "generally". State the fact directly.
* Do not use idioms, metaphors or verdicts, such as "the single most important", "invaluable", "the whole point" or "exactly the kind of". State the fact instead of telling the reader how to feel about it.
  Write "Cray MPICH resolves libfabric through an rpath, not through `LD_LIBRARY_PATH`", not "crucially, and this is the whole point of the tool, Cray MPICH resolves ...".
* Write one topic per paragraph, and keep paragraphs short.
* Use one term for one concept. Do not switch between synonyms for the same thing.
* Use **bold** only for a term at the point where you define it, and for a warning the reader must not miss.
  If a paragraph has more than one or two bold spans, remove all of them. Rewrite the sentence instead, and let the word order carry the emphasis.
* Use a full stop instead of a dash.
  If a sentence joins clauses with dashes, it is usually two sentences.

### Headings are written in sentence case

Use [sentence case](https://en.wikipedia.org/wiki/Letter_case#Sentence_case) for headings. Capitalize only the first word and proper names.

### Avoid nesting headings too deep

You can nest headings up to three levels.

### Lists

Write lists as proper sentences.
If each item is short, separate the items with commas. If the items are longer, or contain multiple sentences, write each item as a full sentence.

1. The first item can look like this,
2. the second like this, and
3. the third item like this.

[](){#ref-contributing-tables}
### Tables

Use a table when several things share the same attributes and the reader wants to compare them. One example is the version of one library across a set of environments.
Use prose or a list for everything else.
A table with a single row is just a sentence in table form. A table whose cells hold several sentences is just prose in table form. Neither is a good use of a table.

* Give every table a header row. Write the header cells in sentence case.
* Keep a cell to a value, a name, or a short phrase.
* Put a unit or a numbering scheme in the header. Do not repeat it in every cell.
* Keep the number of columns small so the table does not scroll sideways on a narrow screen.

Component reference pages under [Packages][ref-pkg] are the one exception.
Each page opens with a two-column table of the same fixed set of properties. This table lets readers compare two components by reading the same rows on each page.
This table is layout, not comparison, and the documentation uses it only on these pages.

### Using admonitions

Use [admonitions](https://squidfunk.github.io/mkdocs-material/reference/admonitions/) for examples, notes and warnings when appropriate.
They stand out from the main text, and you can collapse them by default.

!!! example "Example one"
    This is an example.
    The title of the example uses [sentence case](https://en.wikipedia.org/wiki/Letter_case#Sentence_case).

??? note "Collapsed note"
    This note is collapsed, because it uses `???`.

If you collapse an admonition by default, it must have a title.

The documentation includes some custom admonitions.

#### Change

Use this admonition to record information about a change. It was originally designed to record updates to clusters.

=== "Rendered"
    !!! change "2025-04-17"
        * Slurm was upgraded to version 25.1.
        * uenv was upgraded to v0.8

    Old changes can be folded:

    ??? change "2025-02-04"
        * The new Scratch cleanup policy was implemented.
        * The NVIDIA driver was updated.

=== "Markdown"
    ```
    !!! change "2025-04-17"
        * Slurm was upgraded to version 25.1.
        * uenv was upgraded to v0.8
    ```

    Old changes can be folded:

    ```
    ??? change "2025-02-04"
        * The new Scratch cleanup policy was implemented.
        * The NVIDIA driver was updated.
    ```

### Code blocks

Use [code blocks](https://squidfunk.github.io/mkdocs-material/reference/code-blocks/) to display monospace text, such as source code, terminal output, or configuration files.
The documentation uses [pygments](https://pygments.org) for highlighting.
See the [list of available lexers](https://pygments.org/docs/lexers/#) for the languages you can use in code blocks.

Use [`console`](https://pygments.org/docs/lexers/#pygments.lexers.shell.BashSessionLexer) for interactive sessions with prompt-output pairs:

=== "Markdown"

    ````markdown
    ```console title="Hello, world!"
    $ echo "Hello, world!"
    Hello, world!
    ```
    ````

=== "Rendered"

    ```console title="Hello, world!"
    $ echo "Hello, world!"
    Hello, world!
    ```

!!! warning
    `terminal` is not a valid lexer, but MkDocs and pygments do not warn you when you use it as a language.
    The text renders without highlighting.

!!! warning
    Use `$` as the prompt character. Text can come before it.
    Pygments does not highlight `>` correctly as the prompt character.

The `title=...` attribute gives the code block a heading.

!!! tip
    Include a title that describes what the code block does.

To show commands without their output, use `bash` as the language. This lets readers copy the commands easily:

=== "Markdown"

    ````markdown
    ```bash title="Hello, world!"
    echo "Hello, world!"
    ```
    ````

=== "Rendered"

    ```bash title="Hello, world!"
    echo "Hello, world!"
    ```

### Avoiding repetition using snippets

You can repeat information on different pages to increase visibility for users.
Link to a primary section that describes the topic, instead of repeating the full text on different pages.
If you must repeat content, use [snippets](https://facelessuser.github.io/pymdown-extensions/extensions/snippets/) instead. Snippets keep repeated information synchronized across pages.
Snippets let you include the contents of a text file in multiple places in the documentation.

For example, a text file defines the recommended NCCL environment variables ... The documentation includes this file on multiple pages, because NCCL users must notice and use these environment variables.

Include a snippet with `--8<-- path/to/snippet`.
For example, to include the recommended NCCL environment variables, do the following:

=== "Markdown"

    ````markdown
    ```bash
    ;--8<-- "docs/software/communication/nccl_env_vars"
    ```
    ````

=== "Rendered"

    Note: This example is commented out because the file does not exist.
    We will add this file later.

    ```bash title="Recommended NCCL environment variables"
    ;--8<-- "docs/software/communication/nccl_env_vars"
    ```
