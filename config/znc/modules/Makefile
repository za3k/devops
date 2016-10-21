SOURCES=$(wildcard *.cpp)
SO_FILES=$(SOURCES:.cpp=.so)
all: $(SO_FILES)
clean:
	rm $(SO_FILES)
%.so: %.cpp
	znc-buildmod $^
