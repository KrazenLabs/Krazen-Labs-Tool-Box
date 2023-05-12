# Krazen Labs Tool Box
A collection of personal tools to aid in the creation of 3d avatars.

Currently contains two tools:

## Mesh Joiner

This is just a simple mesh joiner to match my personal workflow. You have to select an Armature and click the button. The tool will then look at all child meshes parented to that armature and join them together. Meshes will be joined by the collection they are in: for each collection, it will join all containing meshes together and name them after that collection. Once done, the meshes wil be put into a "combined" collection (which will be created automatically if it does not exist yet) and the original collection will be disabled. Be aware: the combined collection will be cleared every run, so do not leave anything important in there!

## Unity FBX Exporter

This is a direct implementation from my revised stand-alone Unity FBX Exporter: https://github.com/KrazenLabs/FBXpress-Unity. Instead of the export menu entry, it adds a UI button.
Don't forget to set your export preferences in the scene properties.

The UI is found in the addon panel in the 3D view by pressing N, look for the tab labeled "Krazen Labs".
