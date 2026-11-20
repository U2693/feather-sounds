# feather-sounds

Sound library for the Feather MuseSDK gadget. All clips are mono 22050 Hz MP3.

Served by Vercel as feather-sounds at https://feather-sounds.vercel.app/
- Manifest: index.json
- Listening page: index.html
- Clips: sounds/*.mp3
- Synth sources: synth_bell_chime.py, synth_sad_trombone.py

Vercel serves this statically, no build step. SSO protection is disabled so the Feather can fetch directly.
