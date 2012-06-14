Gallery
=======

A photo gallery made with Django as an application.

Functionality:
Not logged in:
  View albums and pictures.

Logged in:
- Update albums by either adding new or removing old albums.
- When adding or removing albums also add or remove pictures associated with
  that album.
- Rotate pictures to the left or right.
  - When rotating an image, all versions (Original, resized max and thumbnail)
    are rotated with it.
- Add comments to each picture.

Notes:
- All users added to the system are handled the same way and have administrator
  rights.
- When adding albums and pictures, make sure that the user your web server is
  running as has read access to folders and images and that Python have read
  and write access to the same files and folders.
