function createNode($window, $document, text, context) {
    let node = document.createElement('textarea');
    node.style.position = 'absolute';
    node.textContent = text;
    node.style.left = '-10000px';
    node.style.top = (window.pageYOffset || document.documentElement.scrollTop) + 'px';
    return node;
}

function copyNode($document, node) {
    try {
        // Set inline style to override css styles
        document.body.style.webkitUserSelect = 'initial';
        let selection = document.getSelection();
        selection.removeAllRanges();
        node.select();

        if (!document.execCommand('copy')) {
            throw('failure copy');
        }
        selection.removeAllRanges();
    } finally {
        // Reset inline style
        document.body.style.webkitUserSelect = '';
    }
}

export default function copyTextToClipboard(text) {
    let node = createNode(window, document, text, undefined);
    document.body.appendChild(node);
    copyNode(document, node);
    document.body.removeChild(node);
}

