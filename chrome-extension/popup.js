document.addEventListener('DOMContentLoaded', () => {
    const uploadDbBtn = document.getElementById('upload-db-btn');
    const localDbFile = document.getElementById('local-db-file');
    const dbStatusText = document.getElementById('db-status-text');
    const runLocalSqlBtn = document.getElementById('run-local-sql-btn');
    const localSqlEditor = document.getElementById('local-sql-editor');
    const localSqlOutput = document.getElementById('local-sql-output');

    let dbInstance = null; // Holds the sql.js database instance

    if (uploadDbBtn && localDbFile) {
        uploadDbBtn.addEventListener('click', () => localDbFile.click());
        localDbFile.addEventListener('change', handleFileSelect);
    }

    async function handleFileSelect(event) {
        const file = event.target.files[0];
        if (!file) return;

        dbStatusText.innerText = "⏳ Reading file...";
        
        const reader = new FileReader();
        reader.onload = async function() {
            try {
                const uInt8Array = new Uint8Array(this.result);
                
                // Blueprint check for sql.js library availability
                if (window.initSqlJs) {
                    const SQL = await window.initSqlJs({
                        // Required to load wasm helper in extensions
                        locateFile: filename => `sql-wasm.wasm`
                    });
                    dbInstance = new SQL.Database(uInt8Array);
                    dbStatusText.innerText = `🟢 Loaded: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
                    localSqlOutput.innerText = "Database successfully loaded into WebAssembly memory! Ready to query.";
                } else {
                    // Developer sandbox fallback
                    dbStatusText.innerText = `💡 Sandbox Loaded: ${file.name}`;
                    localSqlOutput.innerText = `Success!\n\nTo fully query this file offline, please bundle the official sql.js library as outlined in the chrome-extension/README.md file.`;
                }
            } catch (err) {
                console.error("Error parsing SQLite file:", err);
                dbStatusText.innerText = "❌ Error parsing database file";
                localSqlOutput.innerText = `Error: ${err.message}`;
            }
        };
        reader.readAsArrayBuffer(file);
    }

    if (runLocalSqlBtn && localSqlEditor && localSqlOutput) {
        runLocalSqlBtn.addEventListener('click', () => {
            const query = localSqlEditor.value.trim();
            if (!query) {
                alert("Please write a local SQL query.");
                return;
            }

            if (dbInstance) {
                try {
                    const res = dbInstance.exec(query);
                    if (res.length > 0) {
                        localSqlOutput.innerText = JSON.stringify(res, null, 2);
                    } else {
                        localSqlOutput.innerText = "Query completed successfully. (No rows returned)";
                    }
                } catch (err) {
                    localSqlOutput.innerText = `SQL Error: ${err.message}`;
                }
            } else {
                localSqlOutput.innerText = `Sandbox mode preview for query:\n"${query}"\n\n(Install sql.js per instructions in README.md to execute raw WASM queries privately)`;
            }
        });
    }
});
