.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

================
Back Date Entry
================

Allow back-dated entries across **Sales**, **Purchase**, **Accounting** and
**Stock Transfers** in Odoo 18.

Features
========

* **Sales Orders** — Update confirmation date, delivery scheduled dates and
  draft invoice dates from a single Back Date field.
* **Purchase Orders** — Update order date, receipt scheduled dates and draft
  vendor bill dates automatically.
* **Journal Entries / Invoices** — Override the accounting date and invoice
  date while the entry is in draft state.
* **Stock Transfers (Pickings)** — Override the scheduled date, all stock
  move dates and the effective (done) date.
* **Batch Wizard** — Select multiple records in a list view and apply a back
  date in one step using the *Action → Apply Back Date* menu.
* **Chatter Audit Trail** — Every back-date application is logged in the
  chatter with the date and reason.
* **Future-date warning** — Visual warning when the chosen date is in the
  future.

Usage
=====

1. Open any Sale Order, Purchase Order, Invoice or Transfer.
2. Enter a date in the **Back Date** field (visible on the form).
3. Click **Apply Back Date** in the header buttons.
4. All related records are updated automatically.

For batch updates, select multiple records in a list view and use
**Action ▶ Apply Back Date**.

Configuration
=============

No extra configuration is required. The module installs cleanly on top of
the standard ``sale_management``, ``purchase``, ``account``, and ``stock``
apps.

Author
======

* **Tshering Sherpa** <Tsherings8981@gmail.com>
* LinkedIn: https://www.linkedin.com/in/tshering-sherpa-a17184278/

Changelog
=========

18.0.1.0.0 (Initial Release)
-----------------------------
* Back date field on Sale Order, Purchase Order, Account Move, Stock Picking
* Automatic propagation to linked documents
* Batch wizard with reason/note support
* Chatter audit logging
