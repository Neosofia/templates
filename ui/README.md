# Neosofia UI Registry

This directory contains the central [shadcn/ui](https://ui.shadcn.com/) component registry for Neosofia corporate and product UIs. Instead of relying on a rigidly compiled NPM package containing React components, we govern our components using a registry distribution model.

This gives each frontend app complete local ownership of the components while ensuring the original source (and updates) come with our precise corporate styling, typography, and standard utilities pre-baked in.

## Repository Structure

- `src/components/ui/`: The React / Tailwind UI source components.
- `src/lib/`: Shared pure functions (like `cn` for Tailwind class merging).
- `src/styles/`: Shared generic stylesheets (e.g., our `theme.css` with shadcn CSS variables).
- `scripts/build-registry.mjs`: Compiles the source `.tsx` and `.css` files into a static JSON web registry.

## How it works

When we update or add a component here, running `npm run build` will convert the source files in `src/` into a structure inside `registry/` that the inner shadcn CLI expects to see.

### Using the registry in an app

*(Assuming the `registry/` folder is eventually hosted via a direct static URL, e.g. `https://raw.githubusercontent.com/Neosofia/templates/main/ui/registry`)*

To pull a component directly into a Neosofia repository (e.g., CDP UI):

```bash
# Add a component
npx shadcn add "https://raw.githubusercontent.com/Neosofia/templates/main/ui/registry/ui/button.json"

# Add our utilities 
npx shadcn add "https://raw.githubusercontent.com/Neosofia/templates/main/ui/registry/utils.json"
```

## Adding a new component

1. Copy the raw shadcn component or create your own inside `src/components/ui/`.
2. Apply our dark-theme CSS variable rules (no generic shadcn variables for slate/sky overrides).
3. Run `npm run build`.
4. Commit the changes and the `registry/` output.