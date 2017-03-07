//
//  reader.h
//  LRUAnalyzer
//
//  Created by Juncheng on 5/25/16.
//  Copyright © 2016 Juncheng. All rights reserved.
//

#ifndef reader_h
#define reader_h

#include <stdio.h>
#include <stdlib.h> 
#include <string.h>
#include <sys/types.h>
#include <sys/uio.h>
#include <unistd.h>
#include <glib.h>
#include <stdint.h>
#include <sys/mman.h>
#include <sys/stat.h> 

#include "const.h"
#include "libcsv.h"


#define LINE_ENDING '\n'
#define BINARY_FMT_MAX_LEN 32 


// trace type 
#define CSV 'c' 
#define PLAIN 'p' 
#define VSCSI 'v' 
#define BINARY 'b'  



// data type
#define DT_NUMBER 'l'
#define DT_STRING 'c'



struct break_point{
    GArray* array;
    char mode;
    guint64 time_interval;
};



typedef struct{
    union {
        FILE* file;

        size_t record_size;
        struct{
            void* p;                        /* pointer to memory location, the begin position,
                                             *   this should not change after initilization */
            guint64 offset;                 /* the position the reader pointer currently at */
//            size_t record_size;             /*   the size of one record, used to locate the memory
//                                             *   location of next element */
        };
        // csv reader
        struct{
            FILE *csv_file;
            gboolean has_header;
            unsigned char delim;
            struct csv_parser *csv_parser;
            
            gint real_time_column;          /* column number begins from 0 */
            gint label_column;
            gint op_column;
            gint size_column;
            gint traceID_column; 
            gint current_column_counter;
            
            void* cache_line_pointer;
            gboolean already_got_cache_line;
            gboolean reader_end; 
            
        };
        // binary reader
        struct{
//            guint record_size;            // the size of one record
            char fmt[BINARY_FMT_MAX_LEN];                    // the format of binary reader, using python struct format
            

            gint real_time_pos;          /* position begins from 0 */
            gint label_pos;
            gint size_pos;
            gint current_pos;

        
        };
    };
    char type;                              /* possible types: c(csv), v(vscsi), p(plain text), b(binaryReader)  */
    char data_type;                         /* possible types: l(gint64), c(char*) */
    long long total_num;
    guint64 ts;                             /* current timestamp, record current line, even if some
                                             * lines are not processed(skipped) */
    char file_loc[FILE_LOC_STR_SIZE];
    struct break_point* break_points;
    gint64* reuse_dist;
    gint* last_access;
    guint64 max_reuse_dist;
    GQueue * best_LRU_cache_size;
    double log_base;
    double* hit_rate;
    union{
        struct{
            int vscsi_ver;                  /* version */
        };
    };
    int ver;
    
    
} READER;




typedef struct{
    gpointer item_p;
    char item[cache_line_label_size];
    char type;                              /* type of content can be either guint64(l) or char*(c) */
    guint64 ts;                             /* deprecated, should not use, virtual timestamp */ 
    size_t size;
    int op;
    guint64 real_time;
    gboolean valid;
    unsigned char traceID;                           /* this is for mixed trace */
    void *content;                                   /* the content of page */ 
    guint size_of_content;                           /* the size of mem area content points to */
}cache_line;






READER* setup_reader(char* file_loc, char file_type, char data_type, void* setup_params);
void read_one_element(READER* reader, cache_line* c);
long skip_N_elements(READER* reader, long long N);
int go_back_one_line(READER* reader);
int go_back_two_lines(READER* reader);
void read_one_element_above(READER* reader, cache_line* c);

int read_one_request_all_info(READER* reader, void* storage);
guint64 read_one_timestamp(READER* reader);
void read_one_op(READER* reader, void* op);
guint64 read_one_request_size(READER* reader);


void reader_set_read_pos(READER* reader, double pos);
guint64 get_num_of_cache_lines(READER* reader);
void reset_reader(READER* reader);
int close_reader(READER* reader);
READER* copy_reader(READER* reader);


cache_line* new_cacheline(void);
void destroy_cacheline(cache_line* cp);



#endif /* reader_h */
