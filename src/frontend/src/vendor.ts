/* 
 * Global vendor imports, this is a way to minimize thrashing the cache and keep the main app distribution smaller
 * It also allows pages to access packages globally.
 */

import "./styles/hljs.scss";
import "./styles/hljs-copy.scss";
import hljs from 'highlight.js/lib/core';
// @ts-ignore
import * as hljsCopy from 'highlightjs-copy';

import bash from 'highlight.js/lib/languages/bash';
hljs.registerLanguage('bash', bash);
(window as any).hljs = hljs;
(window as any).hljsCopyPlugin = hljsCopy;
