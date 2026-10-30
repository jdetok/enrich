import argparse
import oracledb # import oracle library and explicitly set client as thick mode is required
oracledb.init_oracle_client(lib_dir="/Users/dekockjt/oracle/instantclient_23_26")

def main():
    print('hello')

if __name__=="__main__":
    main()
