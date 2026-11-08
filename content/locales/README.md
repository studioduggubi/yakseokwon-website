# Website languages

Supported locales: Korean (default), English `/en/`, Traditional Chinese `/zh-TW/` (`zh-Hant`), Japanese `/ja/`.

`catalogue.json` maps stable IDs to current Korean text. Each foreign JSON maps the same IDs to its translation. `ui.json` covers controls created by JavaScript. `config.json` defines language names and routes. Run `scripts/build.py` to create all static pages; missing Korean translation units fail the build. `scripts/verify.py` checks generated pages, local references and noindex directives.

When changing Korean content, update the corresponding source and translations together. Keep the reviewed Japanese terminology 薬食同源 and ヨモギ蒸し, distinguish lotus seeds from leaves and ginseng from carrots, and describe Korean ingredients as Korean-grown. Current client facts: microwave 3 minutes; seated warming 30–40 minutes; abdominal/back warmth totals 1 hour; 8–9 grains including black rice.

The translations cover website text, metadata, navigation, forms, review dialogs and article search. Text printed in original photos, paintings, packaging, posters and source videos remains in the original media. Policy translations reproduce the existing Korean policy as a reference; original template placeholders have not been invented or replaced, and require a separate policy update. Editorial translations are not certified translations or legal review.

Language links preserve the current page and section anchor. Internal navigation stays within the selected locale. Download files and third-party links retain their original destinations. Search indexing remains disabled on every locale.
