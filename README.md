# clean-up-music-artwork
This script modifies how artwork is stored in a music collection. It works to my liking which may not entirely match how you store your artwork. Feel free to modify it as needed.

The goal of the script is to end up with one Cover.jpg file as artwork for each music album. The script provides a dry run option to simulate changes without actually modifying any files.

The script explores your music library recursively and for each music folder:
- Converts Cover.png to Cover.jpg, to save space. If Cover.jpg already exists, overwrites it if the converted Cover.png has a higher resolution. Removes Cover.png.
- Moves Folder.jpg to Cover.jpg for consistency. If Cover.jpg already exists, overwrites it if Folder.jpg has a higher resolution. Removes Folder.jpg.
- If there is no Cover.jpg file, try to extract it from the embedded artwork in the files.
- Remove all embedded artwork to save space.
