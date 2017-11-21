class AccProvider(object):

    def get_num_accounts(self):
        raise Exception("Abstract method!")

    def next(self):
        raise Exception("Abstract method!")
