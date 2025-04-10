### 📁 **ArquivoFolhaPagamento**

**Descrição: Documento que representa a folha de pagamento mensal de funcionários.**

**Dados que o compõem:**

* **Nome do colaborador**
* **Matrícula ou código interno**
* **Cargo / função**
* **Salário bruto**
* **Descontos (INSS, IRRF, faltas, etc.)**
* **Benefícios (vale transporte, alimentação, etc.)**
* **Salário líquido**
* **Competência (mês/ano de referência)**
* **CNPJ da empresa**
* **Assinatura ou campo de validação**


---


### 📁 **ArquivoAdmissao**

**Descrição: Documento gerado no processo de admissão de um colaborador.**

**Dados que o compõem:**

* **Nome completo**
* **CPF**
* **RG**
* **Data de nascimento**
* **Endereço completo**
* **Cargo admitido**
* **Salário acordado**
* **Data de admissão**
* **Assinatura do colaborador e responsável**
* **CNPJ da empresa**
* **Número de registro ou protocolo interno**

### 📁 **ArquivoRescisao**

**Descrição: Termo de encerramento de vínculo empregatício.**

**Dados que o compõem:**

* **Nome do colaborador**
* **CPF**
* **Data de admissão e demissão**
* **Motivo da rescisão**
* **Cálculo de verbas rescisórias (saldo salário, férias, 13º proporcional, etc.)**
* **Descontos aplicáveis**
* **Valor líquido a receber**
* **Data de pagamento**
* **Assinatura do colaborador e empregador**

### 📁 **ArquivoBalanco**

**Descrição: Documento contábil que representa o Balanço Patrimonial.**

**Dados que o compõem:**

* **Ativo (circulante e não circulante)**
* **Passivo (circulante e não circulante)**
* **Patrimônio líquido**
* **Demonstração de lucros e prejuízos acumulados**
* **Período de referência**
* **Assinatura de contador responsável (CRC)**
* **CNPJ da empresa**
* **Notas explicativas (se houver)**

### 📁 **ArquivoNFEEntrada**

**Descrição: Nota Fiscal Eletrônica referente à entrada de mercadorias ou serviços.**

**Dados que o compõem:**

* **Chave de acesso**
* **Nome e CNPJ do fornecedor**
* **Produtos/serviços adquiridos**
* **Quantidade, unidade e valor unitário**
* **Impostos (ICMS, IPI, PIS, COFINS, etc.)**
* **Data de emissão e data de entrada**
* **Número da nota fiscal**
* **Dados do destinatário (empresa)**

### 📁 **ArquivoNFESaida**

**Descrição: Nota Fiscal Eletrônica referente à venda de produtos ou serviços.**

**Dados que o compõem:**

* **Chave de acesso**
* **Nome e CNPJ do cliente**
* **Itens vendidos (produto/serviço, quantidade, valores)**
* **Alíquotas e valores de impostos**
* **Data de emissão**
* **Natureza da operação**
* **Número da nota fiscal**
* **Assinatura digital**

### 📁 **ArquivoModeloDocumento**

**Descrição: Arquivo base usado como template para geração de outros documentos.**

**Dados que o compõem:**

* **Campos variáveis para preenchimento dinâmico (ex: `{{nome}}`, `{{data_admissao}}`)**
* **Formatação textual e visual**
* **Estrutura lógica do documento (seções, cabeçalho, rodapé)**
* **Identificação do tipo de documento (admissão, rescisão, contrato, etc.)**

### 📁 **ArquivoGerado**

**Descrição: Qualquer arquivo de saída criado como resultado de uma função.**

**Dados que o compõem:**

* **Caminho e nome do arquivo gerado**
* **Conteúdo resultante do processamento**
* **Tipo inferido (ex: PDF, DOCX, CSV)**
* **Timestamp de criação**
* **Função que o originou (rastreável pela pipeline)**

### 📁 **ArquivoDeCadastramento**

**Descrição: Arquivo visual (imagem ou PDF) com informações cadastrais de pessoa física ou jurídica.**

**Dados que o compõem:**

* **Nome completo ou razão social**
* **CPF ou CNPJ**
* **Endereço**
* **Documento de identificação (RG, CNH, etc.)**
* **Data de nascimento ou constituição**
* **Assinatura (se presente)**
* **Foto (no caso de imagens de RG ou CNH)**
