import './style.css';
import './article-reading.css';

import $ from 'jquery'

import 'highlight.js/styles/github-dark.css';
import hljs from 'highlight.js';
import mermaid from 'mermaid';

window.$ = window.jQuery = $

var COLOR_MODE_STORAGE_KEY = 'itso-color-mode'
var COLOR_MODES = ['system', 'light', 'dark']

function getSystemColorMode() {
  return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function getStoredColorPreference() {
  try {
    var stored = localStorage.getItem(COLOR_MODE_STORAGE_KEY)
    if (COLOR_MODES.indexOf(stored) !== -1) {
      return stored
    }
  } catch (err) {
    return 'system'
  }
  return 'system'
}

function applyColorPreference(preference) {
  var resolved = preference === 'system' ? getSystemColorMode() : preference
  document.documentElement.setAttribute('data-color-preference', preference)
  document.documentElement.setAttribute('data-color-mode', resolved)
}

function setColorPreference(preference) {
  var safePreference = COLOR_MODES.indexOf(preference) !== -1 ? preference : 'system'
  try {
    localStorage.setItem(COLOR_MODE_STORAGE_KEY, safePreference)
  } catch (err) {
    // Ignore storage failures and keep runtime-only mode.
  }
  applyColorPreference(safePreference)
  updateModeMenuActive()
}

function openModeMenu() {
  var menu = document.getElementById('mode-menu')
  var toggle = document.getElementById('color-mode-toggle')
  if (!menu || !toggle) return
  var rect = toggle.getBoundingClientRect()
  menu.style.top = (rect.bottom + 6) + 'px'
  menu.style.right = (window.innerWidth - rect.right) + 'px'
  menu.style.left = 'auto'
  menu.classList.add('is-open')
  toggle.classList.add('is-open')
  toggle.setAttribute('aria-expanded', 'true')
  updateModeMenuActive()
}

function closeModeMenu() {
  var menu = document.getElementById('mode-menu')
  var toggle = document.getElementById('color-mode-toggle')
  if (menu) menu.classList.remove('is-open')
  if (toggle) {
    toggle.classList.remove('is-open')
    toggle.setAttribute('aria-expanded', 'false')
  }
}

function updateModeMenuActive() {
  var current = document.documentElement.getAttribute('data-color-preference') || 'system'
  var options = document.querySelectorAll('.mode-option')
  for (var i = 0; i < options.length; i++) {
    var opt = options[i]
    if (opt.getAttribute('data-mode') === current) {
      opt.classList.add('is-active')
    } else {
      opt.classList.remove('is-active')
    }
  }
}

function setupColorModeToggle() {
  applyColorPreference(getStoredColorPreference())

  var toggleButton = document.getElementById('color-mode-toggle')
  if (toggleButton) {
    toggleButton.addEventListener('click', function (e) {
      e.stopPropagation()
      var menu = document.getElementById('mode-menu')
      if (menu && menu.classList.contains('is-open')) {
        closeModeMenu()
      } else {
        openModeMenu()
      }
    })
  }

  document.addEventListener('click', function (e) {
    var item = document.querySelector('.nav-mode-item')
    if (item && !item.contains(e.target)) {
      closeModeMenu()
    }
  })

  window.addEventListener('scroll', closeModeMenu, { passive: true })
  window.addEventListener('resize', closeModeMenu)

  var modeOptions = document.querySelectorAll('.mode-option')
  for (var i = 0; i < modeOptions.length; i++) {
    ;(function (opt) {
      opt.addEventListener('click', function (e) {
        e.stopPropagation()
        setColorPreference(opt.getAttribute('data-mode'))
        closeModeMenu()
      })
    })(modeOptions[i])
  }

  if (window.matchMedia) {
    var media = window.matchMedia('(prefers-color-scheme: dark)')
    var onSystemColorModeChange = function () {
      var current = document.documentElement.getAttribute('data-color-preference') || 'system'
      if (current === 'system') {
        applyColorPreference('system')
      }
    }

    if (typeof media.addEventListener === 'function') {
      media.addEventListener('change', onSystemColorModeChange)
    } else if (typeof media.addListener === 'function') {
      media.addListener(onSystemColorModeChange)
    }
  }
}

function slugifyHeading(text) {
  var slug = (text || '').trim().toLowerCase()
  if (slug.normalize) {
    slug = slug.normalize('NFKC')
  }
  return slug
    .replace(/\s+/g, '-')
    .replace(/[^\w\u00c0-\uffff-]/g, '')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
}

function setupArticleReading() {
  var layout = document.getElementById('article-reading-layout')
  var content = document.getElementById('post-content')
  var toc = document.getElementById('post-toc')
  var tocList = document.getElementById('post-toc-list')
  if (!layout || !content || !toc || !tocList) return

  var headings = content.querySelectorAll('h2, h3, h4')
  if (!headings.length) return

  var headingLinkLabel = toc.getAttribute('data-heading-link-label') || 'Link to section'
  var usedIds = {}
  var tocLinks = {}

  for (var i = 0; i < headings.length; i++) {
    var heading = headings[i]
    var headingText = (heading.textContent || '').trim()
    var baseId = heading.id || slugifyHeading(headingText) || ('section-' + (i + 1))
    var headingId = baseId
    var suffix = 2

    while (usedIds[headingId] || (document.getElementById(headingId) && document.getElementById(headingId) !== heading)) {
      headingId = baseId + '-' + suffix
      suffix += 1
    }

    usedIds[headingId] = true
    heading.id = headingId

    var anchor = document.createElement('a')
    anchor.className = 'heading-anchor'
    anchor.href = '#' + encodeURIComponent(headingId)
    anchor.setAttribute('aria-label', headingLinkLabel + ': ' + headingText)
    anchor.textContent = '#'
    heading.appendChild(anchor)

    var item = document.createElement('li')
    item.className = 'post-toc-item post-toc-item--level-' + heading.tagName.slice(1)

    var link = document.createElement('a')
    link.className = 'post-toc-link'
    link.href = '#' + encodeURIComponent(headingId)
    link.textContent = headingText

    item.appendChild(link)
    tocList.appendChild(item)
    tocLinks[headingId] = link
  }

  toc.removeAttribute('hidden')
  layout.classList.add('has-toc')

  var setActiveHeading = function (headingId) {
    var keys = Object.keys(tocLinks)
    for (var i = 0; i < keys.length; i++) {
      tocLinks[keys[i]].classList.toggle('is-active', keys[i] === headingId)
    }
  }

  setActiveHeading(headings[0].id)

  if ('IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function (entries) {
      var visible = []
      for (var i = 0; i < entries.length; i++) {
        if (entries[i].isIntersecting) {
          visible.push(entries[i])
        }
      }
      if (!visible.length) return

      visible.sort(function (a, b) {
        return a.boundingClientRect.top - b.boundingClientRect.top
      })
      setActiveHeading(visible[0].target.id)
    }, {
      rootMargin: '-92px 0px -68% 0px',
      threshold: 0
    })

    for (var j = 0; j < headings.length; j++) {
      observer.observe(headings[j])
    }
  }
}

window.toggleQR = function toggleQR(el) {
  var $target = $(el).closest('.social-link').find('.social-qr')
  if (!$target.length) {
    return
  }
  $('.social-qr').not($target).hide()
  $target.toggle()
}

$(function () {
  setupColorModeToggle()
  setupArticleReading()
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

  $(document).on('click', function (evt) {
    if (!$(evt.target).closest('.social-link').length) {
      $('.social-qr').hide()
    }
  })
})
