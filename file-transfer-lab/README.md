#File Transfer

This supports:

* zero length files
* user attempts to transmit a file which does not exist
* file already exists on the server
* the client or server unexpectedly disconnect
* get files from server
* works w/o stammer proxy

To send a file use `put <filename>`
To download a file use `get <filename>`
