def loadCSS(path):
    cssFile = open(path, "r")
    return f"""<style>{cssFile.read()}</style>"""