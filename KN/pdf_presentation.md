<!-- markdownlint-disable MD033 -->

# PDF Presentation Viewer

This page embeds a PDF as a presentation-style viewer.

<div class="presentation-wrapper">
  <div class="presentation-controls-top">
    <a class="fullscreen-btn" href="../_static/ACME-Kilonova-Toy-Model_Tutorial.pdf" target="_blank" rel="noopener">Apri PDF in nuova scheda</a>
  </div>

  <div class="presentation-container">
    <object
      data="../_static/ACME-Kilonova-Toy-Model_Tutorial.pdf"
      type="application/pdf"
      title="PDF presentation viewer"
      style="width: 100%; height: 78vh; border: 0; background: white;"
    >
      <iframe
        src="../_static/ACME-Kilonova-Toy-Model_Tutorial.pdf"
        title="PDF presentation viewer"
        style="width: 100%; height: 78vh; border: 0; background: white;"
      ></iframe>
      <p>
        <a href="../_static/ACME-Kilonova-Toy-Model_Tutorial.pdf" target="_blank" rel="noopener">
          Apri PDF in nuova scheda
        </a>
      </p>
    </object>
  </div>
</div>

```{note}
This page currently embeds the BAT-Glimpse PDF from the book static assets.
If you want a different document, I can wire this same page to another local asset.
```
