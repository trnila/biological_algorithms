#include <stdio.h>
#include <algorithm>

int c[20];

int main() {
  char a[] = "ABCD";
  int N = 4;
  int i = 0;
      printf("%s\n", a);
  while(i < N) {
//    printf("%d\n", c[i]);
    if(c[i] < i) {
      if(i % 2 == 0) {
        std::swap(a[0], a[i]);
      } else {
        std::swap(a[c[i]], a[i]);
      }

      printf("i=%d ", i);
      for(int j = 0; j < 8; j++) printf("%d ", c[j]);

      printf("%s\n", a);
      fflush(stdout);

      c[i] += 1;
      i = 0;
    } else {
      c[i] = 0;
      i += 1;
    }
  }

}
