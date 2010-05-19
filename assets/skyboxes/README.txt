This directory contains sky textures.
Skies are implemented in form of skyboxes/skycubes in Azure. That means you
have 6 square images that are mapped to a cube (or any other body).

We have some hardcoded naming conventions for these 6 images. These rules
are as follows:
1. Every single sky has its own directory in assets/skyboxes/name
2. In that directory there have to be at least 6 images
3. The file extension has to be one of: .png, .jpg or .tga
4. All six files need to have the same extension.
5. The images need to be named 0-6 plus extension. The single sides are
   mapped this way:

      0.ext -- left
      1.ext -- right
      2.ext -- front
      3.ext -- back
      4.ext -- top
      5.ext -- bottom

There is a template sky with labels on the sides and colored seams.
