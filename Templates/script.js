function insertAfter(novoElemento, elementoBase) {
    elementoBase.parentNode.insertBefore(novoElemento, elementoBase.nextSibling);
}

document.getElementById('btnAdicionarLinha').addEventListener('click', function() {
    const linhaModelo = document.getElementById('linhaModelo'); // seleciona a linha modelo
    const novaLinha = linhaModelo.cloneNode(true); // clona a linha modelo

    const botaoAdicionar = novaLinha.querySelector('#btnAdicionarLinha'); // seleciona o botão de + da nova linha
    botaoAdicionar.remove(); // remove o botão da nova linha

    insertAfter(novaLinha, linhaModelo) // chama a função de inserir a nova linha DEPOIS da linha modelo (esse método não é nativo no DOM)

    // linhaModelo.parentElement.appendChild(novaLinha) // insere a nova linha abaixo da linha modelo MAS abaixo do botão de cadastrar
    
    // linhaModelo.parentElement.insertBefore(novaLinha, linhaModelo); // insere a nova linha acima da linha modelo
});