// Builds the CSS and JavaScript in static/ into build/, which Django serves as
// static files. `node build.mjs --watch` rebuilds when a source file changes.

import { cp, mkdir, readdir, rm, writeFile } from 'node:fs/promises';
import { existsSync, watch } from 'node:fs';
import path from 'node:path';

import * as esbuild from 'esbuild';
import * as sass from 'sass';

const OUT = 'build';

// Third-party files served as they ship: jQuery plugins expect a global
// jQuery, so they are loaded by their own script tags, not bundled.
// [source in node_modules, destination in build/vendor]
const VENDOR = [
  ['jquery/dist/jquery.min.js', 'jquery.min.js'],
  ['parsleyjs/dist/parsley.min.js', 'parsley.min.js'],
  ['select2/dist/js/select2.full.min.js', 'select2.full.min.js'],
  ['select2/dist/css/select2.min.css', 'select2.min.css'],
  ['select2-bootstrap-theme/dist/select2-bootstrap.min.css', 'select2-bootstrap.min.css'],
  ['isotope-layout/dist/isotope.pkgd.min.js', 'isotope.pkgd.min.js'],
  ['imagesloaded/imagesloaded.pkgd.min.js', 'imagesloaded.pkgd.min.js'],
  // pinned to 1.1.2 in package.json: later releases draw the toggle with Font
  // Awesome icons and copy `name` and `required` onto a second, hidden input
  ['bootstrap-show-password/bootstrap-show-password.min.js', 'bootstrap-show-password.min.js'],
  ['bootstrap/dist/css/bootstrap.min.css', 'bootstrap3/css/bootstrap.min.css'],
  ['bootstrap/dist/js/bootstrap.min.js', 'bootstrap3/js/bootstrap.min.js'],
  ['bootstrap/dist/fonts', 'bootstrap3/fonts'],
  ['bootstrap4/dist/css/bootstrap.min.css', 'bootstrap4/css/bootstrap.min.css'],
  // the bundle includes Popper, which Bootstrap 4 requires
  ['bootstrap4/dist/js/bootstrap.bundle.min.js', 'bootstrap4/js/bootstrap.bundle.min.js'],
  ['@fontsource/roboto/latin-400.css', 'roboto/latin-400.css'],
  ['@fontsource/roboto/files/roboto-latin-400-normal.woff2', 'roboto/files/roboto-latin-400-normal.woff2'],
  ['@fontsource/roboto/files/roboto-latin-400-normal.woff', 'roboto/files/roboto-latin-400-normal.woff'],
];

const STYLESHEETS = [
  ['static/css/main.scss', 'css/main.css'],
  ['static/scss/oh-proj-theming.scss', 'css/oh-proj-theming.css'],
];

async function copyVendor() {
  for (const [source, destination] of VENDOR) {
    const from = path.join('node_modules', source);
    const to = path.join(OUT, 'vendor', destination);

    await mkdir(path.dirname(to), { recursive: true });
    await cp(from, to, { recursive: true });

    // minified files name their source map in a trailing comment
    if (existsSync(`${from}.map`)) {
      await cp(`${from}.map`, `${to}.map`);
    }
  }
}

async function buildStylesheets() {
  for (const [source, destination] of STYLESHEETS) {
    const to = path.join(OUT, destination);
    const result = sass.compile(source, { style: 'compressed' });

    await mkdir(path.dirname(to), { recursive: true });
    await writeFile(to, result.css);
  }
}

async function buildScripts() {
  const entries = (await readdir('static/js'))
    .filter((name) => name.endsWith('.js'))
    .map((name) => path.join('static/js', name));

  // one self-contained bundle per page, named after its entry file
  await esbuild.build({
    entryPoints: entries,
    outdir: path.join(OUT, 'js'),
    bundle: true,
    format: 'iife',
    minify: true,
    sourcemap: true,
    target: 'es2017',
    logLevel: 'warning',
  });
}

async function build() {
  await rm(OUT, { recursive: true, force: true });
  await copyVendor();
  await buildStylesheets();
  await buildScripts();
}

await build();

if (process.argv.includes('--watch')) {
  console.log('watching static/ for changes');

  let pending = null;

  watch('static', { recursive: true }, () => {
    clearTimeout(pending);

    pending = setTimeout(async () => {
      try {
        await buildStylesheets();
        await buildScripts();
        console.log('rebuilt');
      } catch (error) {
        console.error(error.message);
      }
    }, 100);
  });
}
