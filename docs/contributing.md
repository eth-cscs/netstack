[](){#ref-contributing}
# Contributing

This documentation is developed using the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) framework.

## Before starting

Please read the [guidelines][] and [style guide][] before making any contribution.
Consistency and common practices make it easier for users to read and navigate the documentation, make it easier for regular contributors to write, and avoid style debates.
We try to strike a balance between following the guidelines and letting authors write in a style that is comfortable for them.

Review your edits checking the [Guidelines][ref-contributing-guidelines] section below.

!!! note
    Note that a simple editor markdown preview may not render all the features of the documentation.

To properly review the docs locally, the `serve` script in the root path of the repository can be used as shown below:
```bash
./serve
...
INFO    -  [08:33:34] Serving on http://127.0.0.1:8000/
```

!!! note
    To run the serve script, you need to first install [uv](https://docs.astral.sh/uv/getting-started/installation/).

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

Adding and maintaining links to internal pages and sections that don't break or conflict requires care.
It is possible to refer to links in other files using relative links, for example `\[the fast server](../servers.md#fast-server)`, however if the target file is moved, or the section title "fast-server" is changed, the link will break.

Instead, we advocate adding unique references to sections.

=== "adding a reference"

    Add a reference above the item, in this case we want to link to the section with the title `## The fast server`:

    ```
    [](){#ref-fast-server}
    ## Fast server
    ```

    Use the `[](){#}` syntax to define the reference/anchor.

    !!! note
        Always place the anchor above the item you are linking to.

=== "linking to a reference"

    In any other file in the project, use the `[][]` syntax to refer to the link (note that this link type uses square braces, instead of the usual parenthesis):

    ```
    [the fast server][ref-fast-server]
    ```

Reference names follow a convention, so that they stay unique across the whole documentation without anyone having to check:

1. A page reference is `ref-` followed by the path of the file, with the `docs/` prefix and the `.md` suffix removed and slashes replaced by hyphens, so `docs/tools.md` is `ref-tools`.
    - The exception is pages under `docs/packages`, which drop the directory name for brevity, so `docs/packages/libfabric.md` is `ref-pkg-libfabric`.
2. An `index.md` page drops the file name, so `docs/analysis/index.md` is `ref-analysis`.
3. A section reference extends the reference of its page with a slug of the section title, so the `## user-stack` section of `docs/tools.md` is `ref-tools-user-stack`.

Every page carries its page reference immediately above the title.
That way any page can be linked to without a relative path, and pages can be moved between directories without touching the links that point at them.

Add a section reference when something links to that section, or when a link to it is likely.
Do not add one above every heading as a matter of course, because unused references are noise in the source and one more thing to keep consistent.

The benefits of this approach are that the link won't break if

* either the file containing the link or the file it refers to moves, or
* the title of the target section changes.

### Images

> A picture is worth a thousand words

We encourage the usage of images to improve clarity and understanding.
You can use **screenshots** or **diagrams**.

Images are stored in the `docs/images` directory.

* Create a new sub-directory for your images if that is appropriate.
* Choose a path and file name that hint at what the image is about. Neither `screenshot.png` nor `PX-202502025-imgx.png` is a great name.

!!! warning
    Keep the size of your images to a minimum because we want to keep an overall lightweight repository.


#### Screenshots

Screenshots are not appropriate for this project.

#### Diagrams

Diagrams can help readers understand more abstract concepts like processes or architectures.
We suggest you use [mermaid](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams#creating-mermaid-diagrams).
That format makes diagrams easy to maintain, and removes the need to commit image files to the repository.

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

If you need more hand-crafted diagrams, we suggest you use [draw.io](https://www.drawio.com/).
Make sure you export the PNG with the [source inside](https://www.drawio.com/doc/faq/export-to-png), typically as a `file.drawio.png`, so that it can be extended later.

### Text formatting

Turn off automatic line breaks in your text editor, and stick to one sentence per line in paragraphs of text.

The examples below show what happens when a change to a sentence forces a line rebalance:

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

    The diff in this case affects the original 3 lines, and creates a new one.

This method defines a canonical representation of text, i.e. there is one and only one way to write a paragraph of text, which plays much better with git.

* Changes to the text are less likely to create merge conflicts.
* Changing one line of text will not modify the surrounding lines, as in the example above.
* Diffs and history are easier to read.

### Frequently asked questions

The documentation does not have a FAQ section, because questions are best answered by the documentation itself rather than in a separate section.
Integrating information into the main documentation takes some care, to identify where the information needs to go and to edit the documentation around it.
Adding the information to a FAQ is easier, but the result is information about a topic distributed between the docs and FAQ questions, which ultimately makes the documentation harder to search.

## Style guide

This section contains general guidelines for how to format and present documentation in this repository.
They should be followed in most cases, but a guideline can be broken, _with good reason_.

[](){#ref-contributing-voice}
### Voice

Write plainly.
Prose that builds up to a point wastes the reader's time, and emphasis that is applied everywhere stops meaning anything.

* State a fact instead of telling the reader how to feel about it.
  Write "Cray MPICH resolves libfabric through an rpath, not through `LD_LIBRARY_PATH`", not "crucially, and this is the whole point of the tool, Cray MPICH resolves ...".
* Reserve **bold** for a term at the point where it is defined, and for a warning that a reader must not miss.
  If a paragraph has more than one or two bold spans, remove all of them and rewrite the sentence so that the word order carries the emphasis.
* Prefer a full stop to a dash.
  A sentence built out of clauses joined by dashes is usually two sentences.
* Avoid superlatives and verdicts, such as "the single most important", "invaluable", "the whole point" and "exactly the kind of".

### Headings are written in sentence case

Use [sentence case](https://en.wikipedia.org/wiki/Letter_case#Sentence_case) for headings, meaning just the first word and names are capitalized.

### Avoid nesting headings too deep

Nesting headings up to three levels is generally ok.

### Lists

Write lists as proper sentences.
Separate the items simply with commas if each item is simple, or make each item a full sentence if the items are longer and contain multiple sentences.

1. The first item can look like this,
2. the second like this, and
3. the third item like this.

[](){#ref-contributing-tables}
### Tables

Use a table when several things share the same set of attributes and the reader wants to compare them, for example the version of one library across a set of environments.
Use prose or a list for everything else.
A table with a single row is a sentence, and a table whose cells hold several sentences is prose in a box.

* Give every table a header row, and write the header cells in sentence case.
* Keep a cell to a value, a name, or a short phrase.
* Put a unit or a numbering scheme in the header rather than repeating it in every cell.
* Keep the number of columns small enough that the table does not need to scroll sideways on a narrow screen.

Component reference pages under [Packages][ref-pkg] are the one exception.
Each of them opens with a two-column table of the same fixed set of properties, so that two components can be compared by reading the same rows on each page.
That table is layout rather than comparison, and it is used only there.

### Using admonitions

Aim to include examples, notes and warnings using [admonitions](https://squidfunk.github.io/mkdocs-material/reference/admonitions/) whenever appropriate.
They stand out better from the main text, and can be collapsed by default if needed.

!!! example "Example one"
    This is an example.
    The title of the example uses [sentence case](https://en.wikipedia.org/wiki/Letter_case#Sentence_case).

??? note "Collapsed note"
    This note is collapsed, because it uses `???`.

If an admonition is collapsed by default, it should have a title.

We provide some custom admonitions.

#### Change

For adding information about a change, originally designed for recording updates to clusters.

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

Use [code blocks](https://squidfunk.github.io/mkdocs-material/reference/code-blocks/) when you want to display monospace text such as source code, terminal output or configuration files.
The documentation uses [pygments](https://pygments.org) for highlighting.
See the [list of available lexers](https://pygments.org/docs/lexers/#) for the languages that you can use for code blocks.

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
    `terminal` is not a valid lexer, but MkDocs or pygments will not warn about using it as a language.
    The text will be rendered without highlighting.

!!! warning
    Use `$` as the prompt character, optionally preceded by text.
    `>` as the prompt character will not be highlighted correctly.

Note the use of `title=...`, which will give the code block a heading.

!!! tip
    Include a title whenever possible to describe what the code block does or is.

If you want to display commands without their output, so that they can easily be copied, use `bash` as the language:

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

It can be useful to repeat information on different pages to increase visibility for users.
If possible, prefer linking to a primary section describing a topic instead of fully repeating text on different pages.
However, if you believe it's beneficial to actually repeat the content, consider using [snippets](https://facelessuser.github.io/pymdown-extensions/extensions/snippets/) to avoid repeated information getting out of sync on different pages.
Snippets allow the contents of a text file to be included in multiple places in the documentation.

For example, the recommended NCCL environment variables are defined in a text file ... and included on multiple pages because it's essential that users of NCCL notice and use the environment variables.

Snippets are included with `--8<-- path/to/snippet`.
For example, to include the recommended NCCL environment variables, do the following:

=== "Markdown"

    ````markdown
    ```bash
    ;--8<-- "docs/software/communication/nccl_env_vars"
    ```
    ````

=== "Rendered"

    Note: this has been commented out, because the file doesn't exist.
    We will expand on this when the time comes.

    ```bash title="Recommended NCCL environment variables"
    ;--8<-- "docs/software/communication/nccl_env_vars"
    ```
