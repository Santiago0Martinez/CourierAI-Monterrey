# Helper ROI Calculator
def calculate_monthly_savings(driver_count, daily_advantage=600):
    return driver_count * daily_advantage * 26

if __name__ == '__main__':
    drivers = 500
    print(f"Monthly savings for {drivers} drivers:  MXN")
