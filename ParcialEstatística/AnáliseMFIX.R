dados <- read.csv(
  "amostravendaEPII.csv",
  sep = ";",
  dec = ","
)

head(dados)
str(dados)

n_pop <- 8092

media_pop <- 101.59
sigma_pop <- 397.90

n_amostra <- 2970
---------------------------------------------------------------------
set.seed(123)

amostra <- dados[
  sample(
    1:nrow(dados),
    size = n_amostra,
    replace = FALSE
  ),
]

amostra$preco_venda <- as.numeric(
  gsub(",", ".", amostra$preco_venda)
) #conversão separador decimal

media_a <- mean(amostra$preco_venda)
sigma_a <- sd(amostra$valor_venda)

confidenttest <-t.test(
  amostra$preco_venda,
  conf.level = 0.95
)

#TESTES DE HIPÓTESE
teste <- t.test(
  amostra$preco_venda,
  mu = media_pop,
  conf.level = 0.95
)

teste$statistic

pvalor<-teste$p.value

mediaobs<-teste$estimate

if(teste$p.value < 0.05){
  print("Rejeita H0")
} else {
  print("Nao rejeita H0")
}


