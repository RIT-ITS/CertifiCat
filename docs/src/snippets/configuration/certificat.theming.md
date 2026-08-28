#### `certificat.theming.global_css` {data-toc-label='global_css' : #certificat.theming.global_css}
<span class="mdx-badge" title=""><span class="mdx-badge__icon">[:material-shape:](../convention#type 'Type')</span><span class="mdx-badge__text">string | null</span></span>


Global CSS injected into a style tag rendered on every page. For example the following section configures the site to use RIT branding:

!!! example

    ```yaml
    certificat:
      theming:
        global_css: |
          html:root {
            --primary-color: #F76902;
            --link-color: #C75300;
            --logo-accent-color: #F76902;
            --neutral-cool-color--100: #D0D3D4;
            --neutral-cool-color--200: #A2AAAD;
            --neutral-cool-color--300: #7C878E;
            --neutral-warm-color--100: #D7D2CB;
            --neutral-warm-color--200: #ACA39A;
            --green-accent-color: #84BD00;
            --lime-accent-color: #C4D600;
            --blue-accent-color: #009CBD;
            --purple-accent-color: #7D55C7;
            --red-accent-color: #DA291C;
            --orange-accent-color: #F6BE00;
            --gray-color--100: #f8f9fa;
            --gray-color--200: #e9ecef;
            --gray-color--300: #dee2e6;
            --gray-color--400: #ced4da;
            --gray-color--500: #adb5bd;
            --gray-color--600: #6c757d;
            --gray-color--700: #495057;
            --gray-color--800: #343a40;
            --gray-color--900: #212529;
            --body-text-color: #212529;
            --font-stack: Helvetica Neue, Helvetica, Arial, sans‑serif;

            --width--small-smartphone: 480px;
            --width--large-smartphone: 768px;
            --width--tiny-desktop: 1000px;
            --width--small-desktop: 1200px;
            --width--max: 1400px;

            --font-size: 16px;
          }

          activity-graph {
            --heat-calendar--start-color: #cff182 !important;
            --heat-calendar--end-color: #fff8a4 !important;
          }
    ```


---
