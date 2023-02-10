<script>
import {
    Collapse,
    Navbar,
    NavbarToggler,
    NavbarBrand,
    Nav,
    NavItem,
    NavLink,
    Dropdown,
    DropdownToggle,
    DropdownMenu,
    DropdownItem
  } from 'sveltestrap';

  let isOpen = false;

  function handleUpdate(event) {
    isOpen = event.detail.isOpen;
  }
</script>

<header>
	<Navbar color="light" light expand="md">
	  <NavbarBrand href="/">BlueSky Web Admin</NavbarBrand>
	  <NavbarToggler on:click={() => (isOpen = !isOpen)} />
	  <Collapse {isOpen} navbar expand="md" on:update={handleUpdate}>
	    <Nav class="ms-auto" navbar>
	      <NavItem>
	        <NavLink href="/enqueued">Enqueued Runs</NavLink>
	      </NavItem>
	      <NavItem>
	        <NavLink href="/about">About</NavLink>
	      </NavItem>
	    </Nav>
	  </Collapse>
	</Navbar>
</header>
