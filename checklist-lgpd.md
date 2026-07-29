# Checklist de Conformidade LGPD (Lei Geral de Proteção de Dados)

**Curso:** Leitura e Interpretação de Desenho Técnico Mecânico  
**Data da Auditoria:** 29/07/2026  
**Escopo:** Material didático digital, scripts JavaScript e armazenamento local  

---

## 1. Verificação de Dados Pessoais

- [x] **Nomes Completos de Alunos:** Nenhum nome real presente.
- [x] **CPF, RG ou Documentos:** Nenhum documento pessoal armazenado ou exibido.
- [x] **E-mails Pessoais:** Nenhum e-mail de aluno cadastrado ou solicitado.
- [x] **Fotos de Alunos:** Nenhuma foto pessoal utilizada.
- [x] **Notas / Desempenho Individual:** Armazenados exclusivamente no navegador local do próprio aluno via `localStorage`.

---

## 2. Princípio de Privacy by Design na Aplicação Web

- [x] **Processamento 100% Local (Client-Side):** Toda a lógica do curso e gamificação roda localmente no navegador do aluno.
- [x] **Zero Chamadas a Servidores Externos:** Nenhum `fetch()`, `XMLHttpRequest` ou script de analytics (Google Analytics, Meta Pixel) enviando dados para a web.
- [x] **Nenhum Cookie de Terceiros:** Apenas `localStorage` local do navegador.
- [x] **Identificadores Genéricos:** O estado armazena apenas chaves genéricas como `senai_desenho_tecnico_mecanico`.
- [x] **Transparência e Controle do Usuário:** Disponibilizado botão de *Reset de Progresso* no menu para que o próprio aluno possa apagar todos os seus dados do navegador quando desejar.

---

## 3. Conclusão da Avaliação LGPD

O aplicativo web cumpre integralmente a LGPD (Lei nº 13.709/2018), garantindo privacidade total aos alunos sem coleta, exposição ou transmissão não autorizada de dados pessoais.
