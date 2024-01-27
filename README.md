This addon will eventually allow Kodi clients to sync playback over the internet in order to watch movies together.
<p>2024-01-22 very early stages, only got it to install properly, show a message box, and post simple json data to firebase.</p>
<p>2024-01-27 The addon is taking shape, it now successfully uploads to firebase realtime database the host's and client's public_ip and external port.
  It also attempts to make a TCP connection (this part hasn't been tested thoroughly yet).
  There is a menu to choose to create or join a session, and the connection information in firebase is encrypted.
  Still a long way to go, but it's getting a shape.</p>
<img src="fanart.png" alt="Artwork" width="100%">
