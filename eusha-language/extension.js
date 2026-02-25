const vscode = require('vscode');
const { exec } = require('child_process');

/**
 * Check if the `elang` command is available in the system PATH.
 * @returns {Promise<boolean>}
 */
function isElangInstalled() {
    return new Promise((resolve) => {
        const cmd = process.platform === 'win32' ? 'where elang' : 'which elang';
        exec(cmd, (error) => {
            resolve(!error);
        });
    });
}

function activate(context) {
    const runCommand = vscode.commands.registerCommand('elang.run', async function () {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No file is open.');
            return;
        }

        const filePath = editor.document.fileName;
        if (!filePath.endsWith('.elang')) {
            vscode.window.showErrorMessage('This is not an Elang (.elang) file.');
            return;
        }

        // Check if elang is installed
        const installed = await isElangInstalled();
        if (!installed) {
            const action = await vscode.window.showErrorMessage(
                'Elang runtime not found. Please install Elang from the official website.',
                'Open Website'
            );
            if (action === 'Open Website') {
                vscode.env.openExternal(vscode.Uri.parse('https://github.com/eusha/elang'));
            }
            return;
        }

        // Save the file before running
        await editor.document.save();

        // Find or create a dedicated "Elang" terminal
        let terminal = vscode.window.terminals.find(t => t.name === 'Elang');
        if (!terminal) {
            terminal = vscode.window.createTerminal('Elang');
        }
        terminal.show();
        terminal.sendText(`elang "${filePath}"`);
    });

    context.subscriptions.push(runCommand);
}

function deactivate() { }

module.exports = {
    activate,
    deactivate
};
