/* 
 * This is a beast, it's well over a megabyte so it's split to another file and loaded on-demand.
 */

import "./styles/easymde.scss";
import EasyMDE from 'easymde';
import CodeMirror from 'codemirror';

window.CodeMirror = CodeMirror;
window.EasyMDE = EasyMDE;
