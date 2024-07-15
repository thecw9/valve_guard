CC	= gcc
CFLAGS += -Wall -g -o1
EXEC 	= main
OBJS 	= main.o

EXTRA_LIBS=-lpthread -L./lib -lrt -lacts3100
$(EXEC) : $(OBJS)
	$(CC) $(OBJS) -o $(EXEC) $(LIBS) $(EXTRA_LIBS) -lm
%.o : %.c
	$(CC) $(FLAGS) -c -g $<

.PHONY : clean
	
clean  :
	rm -rf *.o
	rm -rf $(EXEC) 
	rm -rf *~

