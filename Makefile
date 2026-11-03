# GNU Make, destinado ao Linux. Fontes da aplicação ainda serão implementados.
.DEFAULT_GOAL := help

CC := gcc
CPPFLAGS := -D_POSIX_C_SOURCE=200809L -Isrc
CFLAGS := -std=c11 -Wall -Wextra -Wpedantic -O2 -g
LDFLAGS :=
LDLIBS :=
BUILD_DIR := build

.PHONY: help doctor doctor-dev test-environment build clean

help:
	@printf '%s\n' 'make doctor - verifica todas as ferramentas no ambiente atual' 'make doctor-dev - verifica ferramentas para desenvolvimento C' 'make test-environment - testa o verificador (nao testa a aplicacao)' 'make build - verifica o perfil dev e compila os fontes implementados' 'make clean - remove apenas build/' 'Veja docs/AMBIENTE.md e docs/PLANO_DESENVOLVIMENTO.md.'

doctor:
	bash scripts/check-environment.sh --profile all --json build/environment-all.json

doctor-dev:
	bash scripts/check-environment.sh --profile dev --json build/environment-dev.json

test-environment:
	python3 -m unittest discover -s tests -p 'test_environment.py' -v

build: doctor-dev $(BUILD_DIR)/server $(BUILD_DIR)/client

$(BUILD_DIR)/server: $(BUILD_DIR)/server.o $(BUILD_DIR)/protocol.o | doctor-dev
	$(CC) $(LDFLAGS) -o $@ $^ -pthread $(LDLIBS)

$(BUILD_DIR)/client: $(BUILD_DIR)/client.o $(BUILD_DIR)/protocol.o | doctor-dev
	$(CC) $(LDFLAGS) -o $@ $^ $(LDLIBS)

$(BUILD_DIR)/%.o: src/%.c | doctor-dev
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -pthread -MMD -MP -c $< -o $@

-include $(wildcard $(BUILD_DIR)/*.d)

clean:
	rm -rf -- $(BUILD_DIR)
