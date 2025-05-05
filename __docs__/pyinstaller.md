3. PyInstaller Setup
Now, bundle either wrapper into an executable.

For Tkinter Version
```bash
pyinstaller --onefile --windowed --name "PromptCrafter_Tkinter" tkinter_wrapper.py```

For PyQt Version

```bash
pyinstaller --onefile --windowed --name "PromptCrafter_PyQt" pyqt_wrapper.py```

Include Static/Template Files (Critical for Flask)
If PyInstaller misses Flask’s static/templates, modify the .spec file:

# Add this to the Analysis section in the generated .spec file

```python
datas = [
    ("promptcrafter/static/*", "static"),
    ("promptcrafter/templates/*", "templates"),
]
```
Then rebuild:

```bash
pyinstaller PromptCrafter_Tkinter.spec
```