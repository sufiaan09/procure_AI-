python -c "
open('src/main.jsx', 'w').write('''import React from \"react\"
import ReactDOM from \"react-dom/client\"
import App from \"./App.jsx\"
import \"./index.css\"

ReactDOM.createRoot(document.getElementById(\"root\")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
''')
print('Done')
"