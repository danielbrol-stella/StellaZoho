function insertAfter(novoElemento, elementoBase) {
    elementoBase.parentNode.insertBefore(novoElemento, elementoBase.nextSibling);
}

document.getElementById('btnAdicionarLinha').addEventListener('click', function() {
    const linhaModelo = document.getElementById('linhaModelo'); // seleciona a linha modelo
    const novaLinha = linhaModelo.cloneNode(true); // clona a linha modelo

    const botãoAdicionarVelho = linhaModelo.querySelector('#btnAdicionarLinha'); // seleciona o botão de + da linha modelo
    botãoAdicionarVelho.removeAttribute('id'); // remove o id do botão de + da linha modelo para evitar duplicação de ids
    botãoAdicionarVelho.remove();

    const botaoAdicionarNovo = novaLinha.querySelector('#btnAdicionarLinha'); // seleciona o botão de + da nova linha
    insertAfter(novaLinha, linhaModelo) // chama a função de inserir a nova linha DEPOIS da linha modelo (esse método não é nativo no DOM)

    botaoAdicionarNovo.addEventListener('click', function() {
        const linhaModelo = document.getElementById('linhaModelo');
        const novaLinha = linhaModelo.cloneNode(true);

        const botaoAdicionarNovo = novaLinha.querySelector('#btnAdicionarLinha'); 
        insertAfter(novaLinha, linhaModelo)
    });
});