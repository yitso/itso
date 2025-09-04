
import './style.css';

import $ from 'jquery'

import 'highlight.js/styles/github.css';
import hljs from 'highlight.js';
import mermaid from 'mermaid';

window.$ = window.jQuery = $

$(function () {
  var mermaidBlocks = []
  $('pre > code.language-mermaid').each(function () {
    var rawHtml = $(this).html()
    var decoded = $('<textarea>').html(rawHtml).val()
    var $div = $('<div></div>').addClass('mermaid').text(decoded)
    mermaidBlocks.push({ old: $(this).parent(), new: $div })
  })

  for (var i = 0; i < mermaidBlocks.length; i++) {
    mermaidBlocks[i].old.replaceWith(mermaidBlocks[i].new)
  }

  hljs.highlightAll();

  mermaid.initialize({
    startOnLoad: false,
    theme: 'default'
  })

  ;(async () => {
    await mermaid.run({ querySelector: '.mermaid' })
  })()
})
