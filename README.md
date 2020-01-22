

spine-json-lib
==============

This library was created to parse, edit and optimize spine animations from command line.
[![TravisCI](https://travis-ci.org/socialpoint-labs/spine-json-lib.svg?branch=master)](https://travis-ci.org/socialpoint-labs/spine-json-lib)


Installing
----------

Install and update using `pip`:

     pip install -U spine-json-lib


* Free software: MIT license


Features
----------------

```python
from spine_json_lib import SpineAnimationEditor

animation_editor = SpineAnimationEditor.from_json_file(
    json_path='path/to/animation.json'
)

# images_references will keep references updated to images used in animation
# even after removing an animations or skins
print("{}".format(animation_editor.images_references))

# here we decided to remove "anim1" and "anim2"
animation_editor.erase_animations(
    animations_to_erase=["anim1", "anim2"]
)

# here we remove skin1 and all the images only used on this skin
animation_editor.erase_skins(
    skins_to_erase=["skin1"]
)

# making animation looks twice bigger that it is right now
animation_editor.scale_animation(scaleX=2.0, scaleY=2.0)
```

Credits
-------

This package was created with Cookiecutter and the `audreyr/cookiecutter-pypackage` project template.

Cookiecutter: https://github.com/audreyr/cookiecutter

`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

Contributing
------------

For guidance on how to make a contribution to spine-json-lib, see the `contributing guidelines`.

contributing guidelines: https://github.com/socialpoint-labs/spine-json-lib/blob/master/CONTRIBUTING.rst


Links
-----

* License: `MIT <https://github.com/socialpoint-labs/spine-json-lib/blob/master/LICENSE>`
* Releases: https://pypi.org/project/spine-json-lib/
* Code: https://github.com/socialpoint-labs/spine-json-lib
* Issue tracker: https://github.com/socialpoint-labs/spine-json-lib/issues
