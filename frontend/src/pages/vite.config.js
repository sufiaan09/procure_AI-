python -c "
open('vite.config.js', 'w').write('''import { defineConfig } from \"vite\"
import react from \"@vitejs/plugin-react\"

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      \"/api\": \"http://localhost:8000\"
    }
  }
})
''')
print('Done')
"