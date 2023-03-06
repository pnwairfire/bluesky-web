<script>
  export let pathname = ''

  import { base } from '$app/paths';

  // Note: couldn't get sveltestrap navbar working, so using
  // 'raw' bootstrap classes
  // import {
  //   Collapse, Navbar, NavbarToggler, NavbarBrand, Nav, NavItem,
  //   NavLink, Dropdown, DropdownToggle, DropdownMenu, DropdownItem
  // } from 'sveltestrap';
</script>

<header>
  <nav class="navbar navbar-expand-lg bg-body-tertiary">
    <div class="container-fluid">
      <a class="navbar-brand" href={`${base}`}>BlueSky Web Admin</a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li class="nav-item">
            <a class={`nav-link ${(pathname && pathname.indexOf('/queue') > -1) ? 'active' : ''}`} href={`${base}/queue`}>Worker Queues</a>
          </li>
          <li class="nav-item">
            <a class={`nav-link ${(pathname && pathname.indexOf('/runs') > -1) ? 'active' : ''}`} href={`${base}/runs`}>Runs Database</a>
          </li>
          <li class="nav-item">
            <a class={`nav-link ${(pathname && pathname.indexOf('/stats') > -1) ? 'active' : ''}`} href={`${base}/stats`}>Stats</a>
          </li>
          <li class="nav-item">
            <a class={`nav-link ${(pathname && pathname.indexOf('/about') > -1) ? 'active' : ''}`} href={`${base}/about`}>About</a>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</header>
