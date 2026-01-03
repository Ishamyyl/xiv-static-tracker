import { svelte } from '@sveltejs/vite-plugin-svelte'
import tailwindcss from '@tailwindcss/vite'
import type { UserConfig } from 'vite'

export default {
  plugins: [svelte(), tailwindcss(),],
  build: {
    minify: false,
    lib: {
      entry: {
        app: 'src/app.ts',
        counter: "src/lib/Counter.svelte",
        gear: "src/lib/Gear.svelte",
        group: "src/lib/Group.svelte",
      },
      formats: ['es'],
    }
  },
} satisfies UserConfig
