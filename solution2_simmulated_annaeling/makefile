CC      := gcc
CCFLAGS := -lm -ggdb -pg
LDFLAGS :=

TARGETS:= simulated_annealing
MAINS  := simulated_annealing.o
OBJ    := ../helpers/fitness.o ../helpers/mutations.o ../helpers/playfair.o ../helpers/helpers.o $(MAINS)
DEPS   := ../helpers/fitness.h ../helpers/mutations.h ../helpers/playfair.h ../helpers/counts.h ../helpers/helpers.h

.PHONY: all clean

all: $(TARGETS)

clean:
	rm -f $(TARGETS) $(OBJ)

$(OBJ): %.o : %.c $(DEPS)
	$(CC) -c -o $@ $< $(CCFLAGS)

$(TARGETS): % : $(filter-out $(MAINS), $(OBJ)) %.o
	$(CC) -o $@ $(LIBS) $^ $(CCFLAGS) $(LDFLAGS)
