# Small Plugin for Layer and Style Management

## Introduction
This small Rhino Python plugin adds two commands, Rhss, and ToLayers. To install copy the ```WUtils {c6ae437b-7e42-4e42-b153-7e52d87463b3}``` folder into ```<Rhinoceros Location>/8.0/Plug-ins/PythonPlugIns/WUtils {c6ae437b-7e42-4e42-b153-7e52d87463b3}```.

## ToLayers
Allows the user to move objects from a layer with sublayers to another layer with sublayers whilst maintaing the layer heirarchy. Useful for when similar layer structures are used throughout a document.

## RHSS

This command applies a stylesheet in the RHSS (RHino Style Sheet) format, a format loosley inspired by CSS and Python. This makes it simple to keep a consistent, yet flexible set of styles. Run ```RHSS <filename>.rhss``` to apply the style. Using ``` RHSS Open``` allows the user to select a file.

### RHSS Stylesheet Syntax
The syntax takes insipration from Python, this means indentation is not optional.
The file is divided into blocks of the structure:

```
# Comment
Selector:
    Property: Value
```

Much like in CSS, the selectors cascade with later selectors overwriting
earlier ones.  All selectors are based on the names of the layers and how
they are structured.

#### Patterns

Patterns are parts of selectors which match to layer name parts rather than just whole layers.  The patterns which may be used include:

| Pattern        | Syntax                 | Description                                                  |
| -------------- | ---------------------- | ------------------------------------------------------------ |
| String         | `Layer:`               | Matches any layer with name "Layer".                         |
| Wild Card      | `*:`                   | Match any Layer.                                             |                        |
| Or             | `Pattern1 | Pattern2:` | Match either pattern.                                        |
| Number Capture | `%Name:`               | Match any number.  Number value may be accessed in property descriptions later. |
| Grouping       | `(Pattern):`           | Group parts of the pattern to build more complex patterns.   |
| Child Layers        | `Layer1 ~ Layer2:` | Select if Layer2 is somewhere inside of Layer1 .             |
| Direct Child Layers | `Layer1 > Layer2:` | Select if Layer2 is the direct child of Layer1.              |
| Root Layer          | ` ^ Layer:`        | Select if the layer is a root layer.                         |

It needs to be noted that spaces are not included in patterns.  This removes ambiguity, however it also means that RHSS cannot accept any layers with spaces in their names.

#### More Complex Selector Examples:

These selectors can be combined to match quite complex layer names however it is not recommended to do so.  While patterns and selectors are internally the same, it needs to be noted that once a pattern reaches the selector level it needs to match the entire name of the layer.

| Pattern               | Example Matches                        | Description                                                  |
| --------------------- | -------------------------------------- | ------------------------------------------------------------ |
| `Default`             | Default, Layer::Default                | Selects any layer called "Default" anywhere in the hierarchy of layers. |
| `^ Default`           | Default                                | Will only select a root level layer called "Default"         |
| `* > Default`         | Layer::Default, Layer::Layer::Default  | Will only match a layer called "Default" that is the child of another layer. |
| `Default-%N`          | Default-1, Default-2, Layer::Default-3 | Matches any layer of the pattern "Default" followed by a dash and a number. |
| `(D|d)efault`         | default, Default                       | Select both capitalised and non capitalised default layers.  |
| `Def*`                | Default, Def, Defined                  | Select any layer starting with "Def".                        |
| `^ Default ~ *`       | Defualt::Child::AnotherChild           | Select every layer inside of the root default layer.         |
| `^ Default | Layer`   | Defualt, Layer                         | Select "Default" and "Layer" root layers.                    |
| `(^ Default) | Layer` | Default, Layer, Test::Layer            | Select the root level "Default" and any other layer called Layer. |

#### Properties

The properties correspond to the layer properties except for ZOrder which is manually implemented (currently disabled due to performance issues).  The Alt Names allow for more concise sylesheets. As 

| Property             | Alt Name  | Description                                                  |
| -------------------- | --------- | ------------------------------------------------------------ |
| `LayerColor: Color`  | `Color`   | Color of the layer as shown in Rhino.                        |
| `LineType: String`   | `Pen`     | The type of the line as defined in Rhino Properties.         |
| `Visible: Boolean`   | `Visible` | Whether the layer is visible.                                |
| `PrintWidth: Number` | `Weight`  | The Width of the Line, 0 is defualt, negative numbers do not print. |
| `PrintColor: Color`  | `Ink`     | The color plotted.                                           |
| `ZOrder: Number`     | `Layer`   | How objects are arranged visibly. This is a slow process so its best to avoid if possible. |

The values in the sylesheet are treated as Python expressions and therefore offer a large range of possibilities.  Each expression may used a range of default values and functions to ease the use. These are context dependant and depend on the type of object expected in return for the property. As the functions can access values from their parent, relative properties, such as a linewight twice that of the parent can be implemented. The hash values are useful for assigning unique colours to layers. By default all the functions from the math library are available as well as:

| Property | Alt Name | Description                                              |
| -------- | -------- | -------------------------------------------------------- |
| `Self`   | `S`      | The value that the layer is currently set to.            |
| `Parent` | `P`      | The value that the direct parent of the layer is set to. |
| `H1` | `H1`      | A hash of the name of the layer in the range 0-1. |
| `H255` | `H255`      | A hash of the name of the layer in the range 0-255. |

As well as any values captured using `%Name`.  These will be included under the local variable `Name`.

Additional variables assigned to line weights:

| Name       | Description                              |
| ---------- | ---------------------------------------- |
| `NoPrint`  | Does not print the line.                 |
| `Defalut`  | Prints using Rhino's Default line width. |
| `Hairline` | Prints a Hairline.                       |

Additional functions and variables assigned to color values:

| Name                                 | Description                                                  |
| ------------------------------------ | ------------------------------------------------------------ |
| `hsv(hue, saturation, value, alpha)` | Generate a color using Hue, Saturation ,Value and Alpha.     |
| `xyz(red, green, blue, alpha)`       | Generate RGBA colors Usage is, where these values range from 0 to 1. |
| `rgb(red, green, blue, alpha)`       | Generate RGBA colors Usage is `rgb(red, green, blue, alpha)`, where these values range from 0 to 255. |
| `gray(value)`                        | Generate a greyscale color where 0 is black and 1 is white.  |
| `Color.rot(angle)`                   | Rotate the Hue of a color by angle (0-360).                  |
| `Color.lit(value)`                   | Lighten a color.                                             |
| `Color.fde(value)`                   | Fade or Desaturate a color.                                  |
| `Color.rfl(value)`                   | Reflect a color across the HSV plane.                        |
| `Color.inv(value)`                   | Invert a color.                                              |
| `Color.alpha(value)`                 | Set the Alpha of a color.                                    |
| `Color.x`                            | Get the red value of a color in 0-1 range.                   |
| `Color.y`                            | Get the green value of a color in 0-1 range.                 |
| `Color.z`                            | Get the blue value of a color in 0-1 range.                  |
| `Color.w`                            | Get the alpha value of a color in 0-1 range.                 |
| `Color.r`                            | Get the red value of a color in 0-255 range.                 |
| `Color.g`                            | Get the green value of a color in 0-255 range.               |
| `Color.b`                            | Get the blue value of a color in 0-255 range.                |
| `Color.a`                            | Get the alpha value of a color in 0-255 range.               |
| `Color.h`                            | Get the hue of a color.                                      |
| `Color.s`                            | Get the saturation of a color.                               |
| `Color.v`                            | Get the value of a color.                                    |
| `White`                              | Corresponds to built-in Rhino color of the same name.        |
| `LightGray`                          | Corresponds to built-in Rhino color of the same name.        |
| `Gray`                               | Corresponds to built-in Rhino color of the same name.        |
| `DarkGray`                           | Corresponds to built-in Rhino color of the same name.        |
| `Black`                              | Corresponds to built-in Rhino color of the same name.        |
| `Red`                                | Corresponds to built-in Rhino color of the same name.        |
| `Brown`                              | Corresponds to built-in Rhino color of the same name.        |
| `Orange`                             | Corresponds to built-in Rhino color of the same name.        |
| `Gold`                               | Corresponds to built-in Rhino color of the same name.        |
| `Yellow`                             | Corresponds to built-in Rhino color of the same name.        |
| `Chartreuse`                         | Corresponds to built-in Rhino color of the same name.        |
| `Green`                              | Corresponds to built-in Rhino color of the same name.        |
| `DarkGreen`                          | Corresponds to built-in Rhino color of the same name.        |
| `SeaGreen`                           | Corresponds to built-in Rhino color of the same name.        |
| `Aquamarine`                         | Corresponds to built-in Rhino color of the same name.        |
| `Cyan`                               | Corresponds to built-in Rhino color of the same name.        |
| `Turquoise`                          | Corresponds to built-in Rhino color of the same name.        |
| `Lavender`                           | Corresponds to built-in Rhino color of the same name.        |
| `Blue`                               | Corresponds to built-in Rhino color of the same name.        |
| `DarkBlue`                           | Corresponds to built-in Rhino color of the same name.        |
| `Purple`                             | Corresponds to built-in Rhino color of the same name.        |
| `Magneta`                            | Corresponds to built-in Rhino color of the same name.        |
| `Violet`                             | Corresponds to built-in Rhino color of the same name.        |
| `Pink`                               | Corresponds to built-in Rhino color of the same name.        |