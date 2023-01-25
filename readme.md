
## ������� ������ ���������

������ selenium'�� ��� �����:
- [�.�����](https://www.mvideo.ru/)
- [����](https://www.ozon.ru/)

������ ��������������� ������  **sel_scrap.py**

����� ������ selenium'� �������, � �������� �������� � �����. Headless ����� (��� ������� ��������) �� ���������� �� ����� (��� ����� �����), ������� �������� ��������� � ����������� ���������. � ����� �� chrome (��� ������� ������ ��� ����).


� ���������:
- PAGE_COUNT - ���������� ������� ������� ������ �� ��������
- PARSE_LIST - ������ ������� � ������� ������

�� ������������ sqlite (���� **nb.db**). ��������� ��� �������.
���� � ���������� ������� ��������.

����� ���-5 ������ �� ����� (��� ������ ����� �� �����):
1. [Apple box-apple-6701](https://www.ozon.ru/product/13-3-noutbuk-igrovoy-noutbuk-apple-box-apple-6701-apple-m2-3-5-ggts-ram-512-gb-hdd-apple-m2-829712509) (��� �������� (�� �����!) � ���� ��������� �������, � ������������ �������� �������, ��������� � ������� ����� �� ��������, �� ���� 2000, ������ ��� ������ ����� �� �����)
 2. [TB-N5095-16GB](https://www.ozon.ru/product/15-6-noutbuk-tb-n5095-16gb-intel-celeron-n5095-2-0-ggts-ram-16-gb-ssd-2048-gb-intel-uhd-graphics-669850752)
 3. [GTN5105-12GB-2TB](https://www.ozon.ru/product/16-noutbuk-gtn5105-12gb-2tb-intel-celeron-n5105-2-0-ggts-ram-12-gb-ssd-2048-gb-intel-uhd-graphics-745660157)
 4. [S03](https://www.ozon.ru/product/15-6-noutbuk-s03-amd-ryzen-7-3700u-2-3-ggts-ram-20-gb-ssd-1024-gb-amd-radeon-rx-vega-10-windows-749831517)
 5. [Azerty AZ-1509-1](https://www.ozon.ru/product/15-6-noutbuk-azerty-az-1509-1-intel-celeron-n5095-2-0-ggts-ram-16-gb-ssd-1024-gb-intel-uhd-graphics-781238942) 

���� ��� ���������� �����:
<pre>
|--------------------------------------------|
| �������� | ��� | ����� | ��� | SSD | ����  |
|----------|-----|-------|-----|-----|-------|
|   ���    | 10  |   4   | 15  | 0.5 | 0.005 |
|--------------------------------------------|
</pre>

���� ������ ����������� ��������, ������ �������:
<pre>
            CREATE TABLE IF NOT EXISTS computers(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,
            url varchar,
            visited_at timestamp,
            name varchar,
            cpu_hhz float,
            screen_in float,
            ram_gb int,
            ssd_gb int,
            price_rub int,
            rank float generated always as 
            ( 
                0
                + 10 * cpu_hhz
                + 4 * screen_in
                + 15 * ram_gb
                + 0.5 * ssd_gb 
                - 0.005 * price_rub
                ) stored   
            );
</pre>