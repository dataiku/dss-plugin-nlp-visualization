# Font Build Instructions

The fonts used in this plugin are based on [Noto Fonts](https://github.com/googlefonts/noto-fonts/), an open source multilingual font project created by Google. Fonts can be browsed on the [google.com/get/noto](https://www.google.com/get/noto) website.

Google created one base font, [Noto Sans](https://fonts.google.com/specimen/Noto+Sans), supporting 582 languages. For 
other languages, Google built additional language-based fonts, each of them containing only the glyphs corresponding
to its language. To create a multilingual font, we need to merge those different fonts into one. To do so, Google has also published a series of tools in the [`nototools`](https://github.com/googlefonts/nototools) python package.

However, font files have a limit to their maximum amount of glyphs, so we cannot build one single font file supporting 
all languages. As an example, for Simplified Chinese, the NotoCJKsc font file already contains too many glyphs to be merged. In order to choose which languages to include in our final fonts, we used the [`merge_font.py`](https://github.com/googlefonts/nototools/blob/master/nototools/merge_fonts.py) tool. Note that Google has also provided a [`merge_noto.py`](https://github.com/googlefonts/nototools/blob/master/nototools/merge_noto.py) tool that allows you to merge Noto fonts based on language presets. In our case, it wasn't suiting our needs, hence the use of `merge_font.py`.

Please note that this project is still in development, which adds some limitations to the merged tool. Those limitations are detailed hereafter.

## Nototools install

Please refer to [`nototools`](https://github.com/googlefonts/nototools) README.md

## Merge workflow

In order to use `merge_font.py`, you'll need all your different font files in the same folder. You also need to edit `merge_font.py` to select the list of font files to be merged. Finally, the command to run is: 
    <code>merge_fonts.py -d original_fonts_dir_path -o merged_font_file_path</code>

## Limitations

On 2021-01-20, the Noto project is in [development phase III](https://github.com/googlefonts/noto-fonts/milestones). All fonts are being streamlined to 1000 upem. Previously, fonts were built in 2048 upem.

While Google is migrating all fonts from phase II to phase III, 4 fonts were not yet migrated:
* `NotoSansGujarati-Regular.ttf`
* `NotoSansKannada-Regular.ttf`
* `NotoSansMalayalam-Regular.ttf`
* `NotoSansTelugu-Regular.ttf`

It is impossible to merge phase II and phase III fonts because of their upem differences. So it was impossible to create a single font supporting all languages supported by this plugin. On top of that, for Simplified Chinese, the NotoCJKsc font file already contains too many glyphs to be merged. 

## Merged fonts files details

Consecuently to previous limitations, we reduced the number of font files in this plugin down to 3:

* `NotoSansMerged-Regular-1000upem.ttf`: containing all phase III fonts except from NotoCJKsc
* `NotoSansMerged-Regular-2048upem.ttf`: containing all legacy phase II fonts (for Gujarati, Kannada, Malayalam and Telugu support)
* `NotoSansCJKsc-Regular.otf`: to support Simplified Chinese

Depending on the plugin recipe settings, we choose the adequate font to generate each wordcloud. NB: in order to improve `NotoSansMerged-Regular-2048upem.ttf`'s language support, we added to the font files the [NotoSans-Regular legacy font file from phase II](https://github.com/googlefonts/noto-fonts/releases/tag/v2017-03-06-pre-phase3)

## Original files location

All files used to generate the merged fonts are stored in the resource dir, in the `noto_phase_2` and `noto_phase_3` folders