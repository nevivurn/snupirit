# snupirit

Attend SNU lectures by sending your spirit to the classroom.

## Usage

1. Obtain the x86_64 `libEncryptionKeyStore.so` file.

   ```console
   $ # for reference:
   $ shasum libEncryptionKeyStore.so
   84126efbb85bec19dec85f17c1c8a2298f3ca9af  libEncryptionKeyStore.so
   ```

2. Extract the encryption keys.

   ```console
   $ nix shell github:nevivurn/snupirit -c extract-keys libEncryptionKeyStore.so
   [+] sbox: [omitted]
   [+] keys:
   [*]     [omitted]
   [+] wrote keys.py

   $ # for reference:
   $ shasum keys.txt
   4702346c81f06d88c141df06f94db40b8bc62ad5  keys.txt
   ```

3. Prepare the `config.toml` configuration file. For example:

   ```toml
   # Your student ID.
   student_id = "2017-19937"

   # "20241" for the 2024 spring semeter.
   # You figure out the rest.
   term = "20241"

   # Lecture ID to room number mapping.
   [rooms]
   # You can find the lecture ID in the refresh response.
   # The room number stands for the last three digits of the beacon's SSID.
   # Becaons are named like SNUB765, SNUB760, SNUB767, etc.
   # May require some trial and error to find the right room number.
   217863 = "765"
   217988 = "760"
   217864 = "767"
   ```

4. Run the script within the attendance window.

   ```console
   $ nix run github:nevivurn/snupirit
   ```
